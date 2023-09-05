import io, os, struct
from dataclasses import dataclass
from typing import Callable, List, Optional

from .imagebackup import ImageBackup, ImageBackupException, WrongImageFile, \
                         reportSize, BITS_SET

from tqdm import tqdm # install with "pip install tqdm"; on Ubuntu install with "sudo apt install python3-tqdm"


#######################################################################
#                              Exception                              #
#######################################################################

class PartCloneException(ImageBackupException):
    """
    This exception is raised for any issues encountered
    with the partclone image.
    """
    def __init__(self, s: str):
        super().__init__(s)


#######################################################################
#                              Checksums                              #
#                              =========                              #
# https://github.com/Thomas-Tsai/partclone/blob/master/src/checksum.c #
#######################################################################

def crc(byte: int) -> int:
    "Computes the CRC32_TABLE cached values."
    crc = byte
    for j in range(8):
        crc = (crc >> 1) ^ 0xedb88320 if crc & 1 else crc >> 1
    return crc

CRC32_TABLE = [crc(i) for i in range(256)]

del crc # delete crc function to prevent it from being called instead of crc32

CRC32_SEED = 0xffffffff

def crc32(buffer: bytes, seed = CRC32_SEED) -> int:
    "Compute partclone crc32 for a given buffer."
    crc = seed
    for b in buffer:
        crc = (crc >> 8) ^ CRC32_TABLE[(crc ^ b) & 0xff]
    return crc


#########################################################################
#                              BlockOffset                              #
#########################################################################

@dataclass
class BlockOffset:
    file_offset : int
    "offset into image file"
    cksum_offset: int
    ">= 0 and < PartClone.checksumBlocks()"

#########################################################################
#                               PartClone                               #
#                               =========                               #
# https://github.com/Thomas-Tsai/partclone/blob/master/IMAGE_FORMATS.md #
#########################################################################

class PartClone(ImageBackup):
    """
    The partclone file format is documented in
    https://github.com/Thomas-Tsai/partclone/blob/master/IMAGE_FORMATS.md

    This class reads the header of a partclone image, checks for
    the supported version (version 2), compares the header's crc32, reads
    the bitmap, and verifies the bitmap's crc32.
    """

    READ_SIZE = 110

    CHECKSUM_MODE = { 0: 'NONE', 32: 'CRC32' }
    BITMAP_MODE   = { 0: 'NONE', 1: 'BIT', 8: 'BYTE' }

    BLOCK_OFFSET_SIZE = 1024
    "Allocate an index for every 128 bytes; a reasonable default for indexing."

    def __init__(self, file: io.BufferedIOBase, filename:str,
                 block_offset_size: int = 1024):
        super().__init__(file, filename)

        # read 106-byte header
        buffer = file.read(self.READ_SIZE)
        if buffer[:15] != self.PARTCLONE:
            raise WrongImageFile(f"'{filename}' is not a partclone image. "
                                 f"Command 'file {filename}' can help "
                                 "figure out what kind of file this is.",
                                 buffer)
        self.partclone_version = str(buffer[16:30], 'utf-8')
        if (pos := self.partclone_version.find('\0')) != -1:
            self.partclone_version = self.partclone_version[:pos]
        self.img_version = str(buffer[30:34], 'utf-8')
        if self.img_version != '0002':
            raise PartCloneException(f"Version {self.img_version} not "
                                     "supported; only version 2 is supported.")
        self.endian = struct.unpack('<H', buffer[34:36])[0]
        if self.endian not in [0xc0de, 0xdec0]:
            raise PartCloneException("Unexpected endianness "
                                     f"{self.endian:04x}.")
        self.endian = '<' if self.endian == 0xc0de else '>'
        self.fs_type = str(buffer[36:52], 'utf-8')
        if (pos := self.fs_type.find('\0')) != -1:
            self.fs_type = self.fs_type[:pos]
        self.fs_total_size, self.fs_total_blocks, self.fs_used_blocks, \
            self.fs_used_bitmap, self.fs_block_size, feature_selection, \
            self.image_version, self.cpu_bits, self.checksum_mode, \
            self.checksum_size, self.checksum_blocks, self.checksum_reseed, \
            self.bitmap_mode, self.header_crc32 = \
                struct.unpack(f'{self.endian}4Q2L4HL2BL', buffer[52:110])
        if self.checksum_mode not in [0, 32]:
            raise PartCloneException("Unsupported checksum mode "
                                     f"{self.checksum_mode}; modes 0 and 32 "
                                     "are supported.")
        if self.header_crc32 != (crc := crc32(buffer[:106])):
            raise PartCloneException(f"Header CRC mismatch: "
                                     f"0x{self.header_crc32:8x} != 0x{crc:8x}.")
        # read bitmap
        size = (self.totalBlocks() + 7) // 8
        self.bitmap = file.read(size)
        if len(self.bitmap) != size:
            raise PartCloneException("Unexpected end of file at "
                                   f"{self.READ_SIZE + len(self.bitmap):,}.")
        self.bitmap_crc32 = struct.unpack(f'{self.endian}L', file.read(4))[0]
        if self.bitmap_crc32 != (crc := crc32(self.bitmap)):
            raise PartCloneException("Bitmap CRC mismatch: "
                                     f"0x{self.bitmap_crc32:8x} != 0x{crc:8x}.")
        self.blocks_section = self.READ_SIZE + size + 4
        if block_offset_size % 8 != 0:
            raise PartCloneException(f'Block_offset_size={block_offset_size} '
                                     'must be a multiple of 8.')
        self.block_offset_size = block_offset_size
        self.block_offsets: List[BlockOffset] = []

        if (mod := (self.totalBlocks() % 8)) != 0:
            mask = (1 << mod) - 1
            if (self.bitmap[-1] & mask) != self.bitmap[-1]:
                self.bitmap = self.bitmap[:-1] + bytes([self.bitmap[-1] & mask])

        if (used_blks := sum(BITS_SET[b] for b in self.bitmap if b != 0)) != \
           self.usedBlocks():
            raise PartCloneException(f'{self.usedBlocks():,} blocks in use '
                                     f'according to header but {used_blks:,} '
                                     'found in bitmap.')

    # Header member functions.

    def getTool(self) -> str:
        "Return tool that wrote image."
        return "partclone"

    def fsType(self) -> str:
        "Return file system type, e.g. NTFS or BTRFS."
        return self.fs_type

    def blockSize(self) -> int:
        "Return file system's block size."
        return self.fs_block_size

    def totalSize(self) -> int:
        "Return file system's total size in bytes."
        return self.fs_total_size

    def totalBlocks(self) -> int:
        "Return file system's total size in blocks."
        return self.fs_total_blocks

    def usedBlocks(self) -> int:
        "Return file system's number of blocks in use."
        return max(self.fs_used_bitmap, self.fs_used_blocks)

    def checksumMode(self) -> int:
        "Return checksum mode, 0 (no checksum) or 32 (crc32)."
        return self.checksum_mode

    def checksumSize(self) -> int:
        "Return checksum size (usually 4 bytes)."
        return self.checksum_size

    def checksumBlocks(self) -> int:
        "Return number of blocks preceeding a checksum."
        return self.checksum_blocks

    def checksumReseed(self) -> bool:
        "Reseed crc32 for next checksum or not."
        return bool(self.checksum_reseed)

    def getEndian(self) -> str:
        "Return '<' or '>' for struct.unpack."
        return self.endian

    # Bitmap member functions.

    def bitMap(self) -> bytes:
        "Return the bitmap."
        return self.bitmap

    def blocksSectionOffset(self) -> int:
        "Return offset of Blocks section in image file"
        return self.blocks_section

    def blockInUse(self, block_no: int) -> bool:
        "Returns True if block_no is in use, False otherwise"
        assert block_no >= 0 and block_no // 8 < len(self.bitmap)
        return bool(self.bitmap[block_no // 8] & (1 << (block_no & 7)))

    def buildBlockIndex(self, progress_bar: bool = True):
        """
        Populates index self.block_offsets which is required for
        member function getBlockOffset(). The `progress_bar` argument is
        ignored as building the index from a bitmap is quick.
        """
        if self.block_offsets:
            return
        file_offset = self.blocksSectionOffset()
        block_size = self.blockSize()
        checksum_mode = self.checksumMode()
        checksum_blocks = self.checksumBlocks()
        checksum_size = self.checksumSize()
        blocks_chksum = 0
        block_offset = BlockOffset(file_offset, 0)
        for idx1 in range(0, len(self.bitmap), self.block_offset_size // 8):
            if file_offset != block_offset.file_offset:
                block_offset = BlockOffset(file_offset, blocks_chksum)
            self.block_offsets.append(block_offset)
            idx2 = min(idx1+self.block_offset_size // 8, len(self.bitmap))
            inuse_blocks = sum(BITS_SET[b] for b in self.bitmap[idx1:idx2]
                               if b != 0)
            blocks_chksum += inuse_blocks
            file_offset += block_size * inuse_blocks
            if checksum_mode and checksum_blocks:
                if blocks_chksum >= checksum_blocks:
                    file_offset += checksum_size * (blocks_chksum //
                                                    checksum_blocks)
                    blocks_chksum %= checksum_blocks

    def getBlockOffset(self, block_no: int) -> Optional[int]:
        "Return offset of block in image file or None if block is not in use"

        if not self.blockInUse(block_no):
            return None

        if not self.block_offsets:
            self.buildBlockIndex()

        block_size      = self.blockSize()
        checksum_mode   = self.checksumMode()
        checksum_blocks = self.checksumBlocks()
        checksum_size   = self.checksumSize()

        block_offset_idx = block_no // self.block_offset_size
        block_offset     = self.block_offsets[block_offset_idx]

        bm_idx1          = block_offset_idx * (self.block_offset_size // 8)
        bm_idx2          = block_no // 8

        file_offset      = block_offset.file_offset
        blocks_cksum     = block_offset.cksum_offset

        inuse_blocks = sum(BITS_SET[b] for b in
                           self.bitmap[bm_idx1:bm_idx2] if b != 0) + \
                       BITS_SET[self.bitmap[bm_idx2] & ((1 << (block_no%8))-1)]
        blocks_cksum += inuse_blocks
        file_offset += block_size * inuse_blocks
        if checksum_mode and checksum_blocks:
            if blocks_cksum >= checksum_blocks:
                file_offset += checksum_size * (blocks_cksum // checksum_blocks)
        return file_offset

    def blockReader(self, progress_bar: bool = True, verify_crc: bool = False,
                    fn: Optional[Callable[[int,bytes],None]] = None) -> None:
        """
        Reads all used blocks and verifies all checksums. If **fn** is not
        *None* it will be called for each block.

        :param file: A binary file opened for reading. This can be a regular
        file, a pipe, or a socket. This function will read the file
        sequentially.
        :type file: io.BufferedReader

        :param progress_bar: Whether or not to show progress bar while reading
        blocks; *True* by default.
        :type progress_bar: bool = True

        :param verify_crc: Whether or not to compute and verify checksums while
        reading blocks; *False* by default.
        :type verify_crc: bool = False

        :param fn: An optional function that is called with two parameters, the
        offset into the partition and the data for each block. *None* by
        default.
        :type fn: Optional[Callable[[int,bytes],None]] = None
        """
        with tqdm(total=self.usedBlocks(), unit=' used blocks',
                  unit_scale=True, disable=not progress_bar) as progress:
            endian = self.getEndian()
            block_size = self.blockSize()
            checksum_mode = self.checksumMode()
            checksum_blocks = self.checksumBlocks()
            checksum_size = self.checksumSize()
            checksum_reseed = self.checksumReseed()
            seed = CRC32_SEED
            block_no = blocks_read = prev_blocks_read = 0
            for byte in self.bitMap():
                if block_no % 4096 == 0:
                    if blocks_read > prev_blocks_read:
                        progress.update(blocks_read - prev_blocks_read)
                        prev_blocks_read = blocks_read
                if byte == 0:
                    block_no += 8
                    continue
                for bit in range(8):
                    if byte & (1 << bit):
                        block = self.file.read(block_size)
                        if len(block) != block_size:
                            raise PartCloneException('Unexpected end of file at'
                                                     f' {self.file.tell():,}.')
                        blocks_read += 1
                        if checksum_mode == 32:
                            seed = crc32(block, seed) if verify_crc else -1
                            if checksum_blocks and \
                               blocks_read % checksum_blocks == 0:
                                crc = struct.unpack(f'{endian}L',
                                               self.file.read(checksum_size))[0]
                                if seed != -1 and crc != seed:
                                    msg = 'Blocks CRC mismatch at file offset '\
                                         '{self.file.tell()-checksum_size:,}: '\
                                          f'0x{crc:8x} != 0x{seed:8x}.'
                                    raise PartCloneException(msg)
                                if checksum_reseed:
                                    seed = CRC32_SEED
                        if fn is not None:
                            fn(block_no * block_size, block)
                    block_no += 1
            if blocks_read > prev_blocks_read:
                progress.update(blocks_read - prev_blocks_read)

        # Final CRC check
        if checksum_mode:
            if checksum_blocks and blocks_read % checksum_blocks != 0:
                crc = struct.unpack(f'{endian}L',
                                    self.file.read(checksum_size))[0]
                if seed != -1 and crc != seed:
                    msg = 'Blocks CRC mismatch at file offset '\
                          f'{self.file.tell()-checksum_size:,}: '\
                          f'0x{crc:8x} != 0x{seed:8x}.'
                    raise PartCloneException(msg)

        # End-of-file expected.
        block = self.file.read(block_size)
        if len(block) != 0:
            info = '1 byte' if len(block) == 1 else \
                       'at least 1 block' if len(block) == block_size else \
                           f'{len(block)} bytes'
            raise PartCloneException(f"Error '{self.filename}': {info} of "
                                     "unexpected data after end of backup.")

    def __str__(self) -> str:
        return 'Partclone Header\n================\n' \
               f'partclone version {self.partclone_version}\n' \
               f'fs type           {self.fs_type}\n' \
               f'fs total size     {self.fs_total_size:,} ' \
               f'({reportSize(self.fs_total_size)})\n' \
               f'fs total blocks   {self.fs_total_blocks:,}\n' \
               f'fs used blocks    {self.fs_used_blocks:,} ' \
               f'({reportSize(self.fs_used_blocks * self.fs_block_size)})' \
               '\tused block count based on super-block\n' \
               f'fs_used_bitmap    {self.fs_used_bitmap:,} ' \
               f'({reportSize(self.fs_used_bitmap * self.fs_block_size)})' \
               '\tused block count based on bitmap\n' \
               f'fs block size     {self.fs_block_size}\n' \
               f'image version     {self.image_version}\n' \
               f'cpu bits          {self.cpu_bits}\n' \
               f'checksum mode     ' \
               f'{self.CHECKSUM_MODE.get(self.checksum_mode)}\n' \
               f'checksum size     {self.checksum_size}\n' \
               f'checksum blocks   {self.checksum_blocks}\n' \
               f'checksum reseed   {self.checksumReseed()}\n' \
               f'bitmap mode       {self.BITMAP_MODE.get(self.bitmap_mode)}\n' \
               f'header_crc32      0x{self.header_crc32:08x}\n' \
               f'bitmap            {len(self.bitmap):,} bytes ' \
               f'({reportSize(len(self.bitmap))})\n' \
               f'bitmap_crc32      0x{self.bitmap_crc32:08x}\n' \
               f'blocks_section    at {self.blocks_section:,} in img file\n' \
               f'block_offset_size {self.block_offset_size}\n' \
               f'block_offsets     {len(self.block_offsets):,} instances'
