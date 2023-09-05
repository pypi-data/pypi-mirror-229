import io
from typing import Callable, Optional


#######################################################################
#                              Exceptions                             #
#######################################################################

class ImageBackupException(Exception):
    """
    This exception is raised for any issues encountered
    with reading the backup image.
    """
    def __init__(self, msg: str):
        super().__init__(msg)

class WrongImageFile(ImageBackupException):
    """
    This exception is raised when the image file is not the expected format.
    """    
    def __init__(self, msg: str, magic: bytes):
        super().__init__(msg)
        self.magic = magic

    def getMagic(self):
        "Return data that has already been read from the image file."
        return self.magic


#######################################################################
#                          Numbers of Bits Set                        #
#######################################################################

BITS_SET = [bin(i).count('1') for i in range(256)]
"""The number of bits set for each byte."""


#######################################################################
#                              ImageBackup                            #
#######################################################################

class ImageBackup:
    """
    Base class of *PartClone* and *NtfsCLone*. This base class stores the file
    and file name.

    :param file: Binary file opened for input.
    :type file: io.BufferedIOBase

    :param filename: The open file's name.
    :type filename: str
    """

    PARTCLONE = b'partclone-image'
    PARTIMAGE = b'PaRtImAgE-VoLuMe'
    NTFSCLONE = b'\0ntfsclone-image'

    GZIP  = 0x8b1f
    BZIP2 = 0x5a42
    ZSTD  = 0xb528
    XZ    = 0x37fd
    LZMA  = 0x005d
    LZ4   = 0x2204

    def __init__(self, file: io.BufferedIOBase, filename: str):
        self.file = file
        self.filename = filename

    def getFile(self) -> io.BufferedIOBase:
        """
        Return open binary file.

        :returns: open binary file.
        """
        return self.file

    def getFilename(self) -> str:
        """
        Return name of open binary file.

        :returns: name of open binary file.
        """
        return self.filename

    def getTool(self) -> str:
        """
        Return tool for image backups.

        :returns: string *'ntfsclone'*, *'partclone'*, or *'partimage'*.
        """
        return 'n/a'

    def fsType(self) -> str:
        """
        Return file system type.

        :returns: an upper-case string like *'NTFS'* or *'BTRFS'*.
        """
        return ''

    def blockSize(self) -> int:
        """
        Return file system's block size.

        :returns: size of file system block in bytes.
        """
        return -1

    def totalSize(self) -> int:
        """
        Return file system's total size in bytes.

        :returns: file system's total size in bytes.
        """
        return -1

    def totalBlocks(self) -> int:
        """
        Return file system's total number of blocks.

        :returns: file system's total number of blocks.
        """
        return -1

    def usedBlocks(self) -> int:
        """
        Return file system's number of blocks in use.

        :returns: file system's number of blocks in use.
        """
        return -1

    def bitMap(self) -> Optional[bytes]:
        """
        Return the bitmap for image files that have bitmaps, *None* otherwise.

        :returns: bitmap or *None*.
        """
        return None

    def blocksSectionOffset(self) -> int:
        """
        Return offset of Blocks section in image file.

        :returns: the offset of the very first in-use block in the image file.
        """
        return -1

    def blockInUse(self, block_no: int) -> bool:
        """
        Returns *True* if *block_no* is in use, *False* otherwise.

        :param block_no: block number
        :type block_no: int
        :returns: *True* if *block_no* is in use, *False* otherwise.
        :raises partclone.imagebackup.ImageBackupException: if the block number is out of range.
        """
        raise ImageBackupException(f'Method blockInUse({block_no:,}) '
                                   'not implemented.')
        return False

    def buildBlockIndex(self, progress_bar: bool = True) -> None:
        """
        Builds an index of available blocks. This is done unless the image is
        going to be read only sequentially.

        :param progress_bar: whether to show a progress bar while indexing the blocks.
        :type progress_bar: bool = True
        """
        return None

    def getBlockOffset(self, block_no: int) -> Optional[int]:
        return None

    def blockReader(self, progress_bar: bool = True, verify_crc: bool = False,
                    fn: Optional[Callable[[int,bytes],None]] = None) -> None:
        """
        Reads all used blocks and verifies all checksums. If **fn** is not
        *None* it will be called for each block.

        :param progress_bar: Whether or not to show progress bar while reading blocks; *True* by default.
        :type progress_bar: bool = True

        :param verify_crc: Whether or not to compute and verify checksums while reading blocks; *False* by default.
        :type verify_crc: bool = False

        :param fn: An optional function that is called with two parameters, the offset into the partition and the data for each block. *None* by default.
        :type fn: Optional[Callable[[int,bytes],None]] = None
        """
        return None


def reportSize(size: int) -> str:
    """
    Report size in appropriate unit (B, KB, MB, GB, TB, ...).

    :param size: Size in bytes to be reported.
    :type size: int
    :returns: size as string notation with appropriate unit.
    """
    units = [ 'B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB' ]
    for k in range(len(units)-1, -1, -1):
        if k == 0:
            return f'{size} {units[k]}'
        sz_unit = 1 << (k * 10)
        if size >= sz_unit:
            return f'{size/sz_unit:.1f} {units[k]}'
    assert False
