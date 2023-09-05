#!/usr/bin/env python3

import argparse, bz2, gzip, io, os, struct, sys
from dataclasses import dataclass
from typing import Callable, List, Optional

from .imagebackup import ImageBackup, ImageBackupException, WrongImageFile, \
                         reportSize

from tqdm import tqdm # install with "pip install tqdm"; on Ubuntu install with "sudo apt install python3-tqdm"
import pyzstd         # install with "pip install pystd"

class NtfsCloneException(ImageBackupException):
    """
    This exception is raised for issues encountered when reading ntfsclone
    images.
    """
    def __init__(self, s: str):
        super().__init__(s)

@dataclass
class ClusterRange:
    "Cluster ranges are used for indexing."

    used  : bool
    "Are the clusters in this range used or unused?"

    start : int
    "Starting cluster number."

    size  : int
    "Number of consecutive clusters in this range."

    offset: int
    """
    For used clusters, the offset into the image file for cluster `start`,
    -1 for unused clusters.
    """

    def end(self) -> int:
        "Returns the cluster after the last one in this cluster range."
        return self.start + self.size


class ClusterIndex:
    """
    This class implements the lookup of its offset in the image file for a
    cluster number. Cluster ranges are stored in an array. Binary search in
    this array is used to look up a cluster's offset in the image file.
    """

    def __init__(self, cluster_size: int):
        self.cluster_size = cluster_size
        self.cluster_ranges: List[ClusterRange] = []

    def append(self, range: ClusterRange):
        "Append a cluster range."
        if self.cluster_ranges:
            assert range.start == self.cluster_ranges[-1].end()
        self.cluster_ranges.append(range)

    def offset(self, cluster: int) -> Optional[int]:
        """
        Return the offset for given cluster in the image file if
        the cluster is used. For unused clusters, None is returned.
        """
        # Binary search in cluster ranges.
        l = 0
        r = len(self.cluster_ranges)
        while l < r:
            m = (l + r) // 2
            if cluster < self.cluster_ranges[m].start:
                r = m
            else:
                l = m
                if cluster < self.cluster_ranges[m].end():
                    break
        cr = self.cluster_ranges[l]
        assert cluster >= cr.start and cluster < cr.end()
        # Return offset or None.
        if cr.used:
            return cr.offset + (cluster - cr.start) * (self.cluster_size + 1)
        return None

    def __len__(self):
        return len(self.cluster_ranges)


class NtfsClone(ImageBackup):
    "This class reads and processes an ntfsclone image file."

    HEADER_SIZE = 50
    MAGIC_SIZE  = len(ImageBackup.NTFSCLONE)
    VER_MAJOR   = 10
    VER_MINOR   = 1

    def __init__(self, file: io.BufferedIOBase, filename: str):
        super().__init__(file, filename)

        self.buffer = file.read(self.HEADER_SIZE)

        if len(self.buffer) < self.HEADER_SIZE:
            raise NtfsCloneException(f'Failed to read 50-byte header.')

        if self.buffer[:self.MAGIC_SIZE] != ImageBackup.NTFSCLONE:
            raise WrongImageFile(f'Not an ntfsclone image.', self.buffer)

        self.major_ver, self.minor_ver, self.cluster_size, self.device_size, \
            self.nr_clusters, self.inuse, self.offset_to_image_data = \
                struct.unpack('<2BL3QL', self.buffer[self.MAGIC_SIZE:])

        # Reject different major version, warn if different minor version.
        if self.major_ver != self.VER_MAJOR:
            raise WrongImageFile(f'Major version {self.major_ver} not '
                                 f'supported; {self.VER_MAJOR} supported.',
                                 self.buffer)
        if self.minor_ver != self.VER_MINOR:
            print(f'Warning: minor version {self.minor_ver} not supported; '
                  f'parsing as {self.VER_MAJOR}.{self.VER_MINOR} image file.')

        self.cluster_index = ClusterIndex(self.cluster_size)

        # Skip (usually 6 bytes) to offset_to_image_data.
        file.read(self.offset_to_image_data - self.HEADER_SIZE)

    def buildBlockIndex(self, progress_bar: bool = True) -> None:
        """
        Populates index self.cluster_index which is required for
        member function getBlockOffset().

        ntfsclone images do not have bitmaps. Indexing an image file requires
        us to read the entire image file and not just a bitmap.
        """
        if len(self.cluster_index):
            return
        self.file.seek(self.offset_to_image_data)
        cur_range = ClusterRange(False, 0, 0, -1)
        offset    = self.offset_to_image_data
        with tqdm(total=self.usedBlocks(), unit=' used blocks',
                  unit_scale=True, disable=not progress_bar) as progress:
            cluster = blocks_read = prev_blocks_read = 0
            while True:
                cmd = self.file.read(1)
                if len(cmd) == 0:
                    break
                offset += 1

                if cmd[0] == 0:
                    # Cluster is unused. Read # of consecutive unused clusters.
                    count = struct.unpack('<Q', self.file.read(8))[0]
                    offset += 8
                    if cluster:
                        self.cluster_index.append(cur_range)
                    cur_range = ClusterRange(False, cluster, count, -1)
                    cluster += count
                elif cmd[0] == 1:
                    assert offset == self.file.tell()
                    if cluster > self.nr_clusters:
                        raise NtfsCloneException('Error: Image file corrupted '
                                                 f'(cluster={cluster}).')
                    # read cluster at index cluster
                    self.file.read(self.cluster_size)
                    if cur_range.used:
                        assert cluster == cur_range.end()
                        cur_range.size += 1
                    else:
                        if cluster:
                            self.cluster_index.append(cur_range)
                        cur_range = ClusterRange(True, cluster, 1, offset)
                    offset += self.cluster_size
                    cluster += 1
                    blocks_read += 1
                    if blocks_read % 4096 == 0:
                        progress.update(blocks_read - prev_blocks_read)
                        prev_blocks_read = blocks_read
                else:
                    raise NtfsCloneException('Image file corrupted '
                                             f'(sync={cmd[0]}).')
            self.cluster_index.append(cur_range)
            progress.update(blocks_read - prev_blocks_read)
            prev_blocks_read = blocks_read

    def getBlockOffset(self, block_no: int) -> Optional[int]:
        "Return offset of block in image file or None if block is not in use"

        if block_no > self.nr_clusters:
            raise NtfsCloneException(f'Cluster {block_no} out of range.')

        if len(self.cluster_index) == 0:
            self.buildBlockIndex()

        return self.cluster_index.offset(block_no)

    def getTool(self) -> str:
        "Return tool for image backups, 'ntfsclone'."
        return 'ntfsclone'

    def fsType(self) -> str:
        "Return file system type NTFS."
        return 'NTFS'

    def totalBlocks(self) -> int:
        "Return file system's total size in blocks."
        return self.nr_clusters

    def usedBlocks(self) -> int:
        "Return file system's number of blocks in use."
        return self.inuse

    def blockSize(self) -> int:
        "Return file system's block size."
        return self.cluster_size

    def totalSize(self) -> int:
        "Return file system's total size in bytes."
        return self.device_size

    def blockReader(self, progress_bar: bool = True, verify_crc: bool = False,
                    fn: Optional[Callable[[int,bytes],None]] = None) -> None:
        """
        Reads all used blocks. If **fn** is not *None* it will be called for
        each block.

        :param progress_bar: Whether or not to show progress bar while reading
        blocks; *True* by default.
        :type progress_bar: bool = True

        :param verify_crc: Whether or not to compute and verify checksums while
        reading blocks; *False* by default. Ignored as *ntfsclone* images don't
        contain checksums.
        :type verify_crc: bool = False

        :param fn: An optional function that is called with two parameters, the
        offset into the partition and the data for each block. *None* by
        default.
        :type fn: Optional[Callable[[int,bytes],None]] = None
        """
        with tqdm(total=self.usedBlocks(), unit=' used blocks',
                  unit_scale=True, disable=not progress_bar) as progress:
            cluster = blocks_read = prev_blocks_read = 0

            while True:
                cmd = self.file.read(1)
                if len(cmd) == 0:
                    break

                if cmd[0] == 0:
                    # Cluster is unused. Read # of consecutive unused clusters.
                    count = struct.unpack('<Q', self.file.read(8))[0]
                    cluster += count
                elif cmd[0] == 1:
                    if cluster > self.nr_clusters:
                        raise NtfsCloneException('Image file corrupted '
                                                 f'(cluster={cluster}).')
                    block = self.file.read(self.cluster_size)
                    if fn is not None:
                        fn(cluster * self.cluster_size, block)
                    cluster += 1

                    blocks_read += 1
                    if blocks_read % 4096 == 0:
                        progress.update(blocks_read - prev_blocks_read)
                        prev_blocks_read = blocks_read
                else:
                    raise NtfsCloneException('Image file corrupted '
                                             f'(sync={cmd[0]}).')
            progress.update(blocks_read - prev_blocks_read)
            prev_blocks_read = blocks_read

    def __str__(self):
        return 'NtfsClone Header\n================\n' \
               f'major_ver           : {self.major_ver}\n' \
               f'minor_ver           : {self.minor_ver}\n' \
               f'cluster_size        : {self.cluster_size:,}\n' \
               f'device_size         : {self.device_size:,} ' \
               f'({reportSize(self.device_size)})\n' \
               f'nr_clusters         : {self.nr_clusters:,}\n' \
               f'inuse               : {self.inuse:,} ' \
               f'({reportSize(self.inuse * self.cluster_size)})\n' \
               f'offset_to_image_data: {self.offset_to_image_data}'


###########################################################################
#                 Main Program for Utility vntfsclone                     #
###########################################################################

from .partclone import PartClone
from .fuse import runFuse, isEmptyDirectory, isRegularFile

def compressedMsg(filename: str, compression: str) -> str:
    """
    Formats the error message for compressed images encountered when reading
    image.
    """

    # Suggest an output file name that does not already exist.
    out_name = os.path.split(filename)[1].replace('.'+compression, '')
    if out_name == filename or not out_name.endswith('.img') or \
       os.path.exists(out_name):
        if os.path.exists(out_name + '.img'):
            i = 1
            while os.path.exists(out_name + f'_{i}.img'):
                i += 1
            out_name = out_name + f'_{i}.img'
        else:
            out_name += '.img'

    if compression == 'gz':
        msg = "File '{n1}' is gzip-compressed; run 'gunzip < {n1} > {n2}' " \
              "and try again with '{n2}'."
    elif compression == 'bz2':
        msg = "File '{n1}' is bzip2-compressed; run 'bunzip2 < {n1} > {n2}' " \
              "and try again with '{n2}'."
    else:
        msg = "File '{n1}' is {c}-compressed; run 'zstd -d " \
              "--format={c} -o {n2} {n1}' and try again with '{n2}'."

    return msg.format(msg, n1=filename, n2=out_name, c=compression)


def readImage(file: io.BufferedIOBase, sequential: bool, name: str,
              fn: Callable[[io.BufferedIOBase],ImageBackup]) -> ImageBackup:
    try:
        return fn(file)
    except WrongImageFile as e:
        magic = e.getMagic()
        if magic[:len(ImageBackup.NTFSCLONE)] == ImageBackup.NTFSCLONE:
            if isRegularFile(file):
                file.seek(0)
                return readImage(file, sequential, name,
                                 lambda f:NtfsClone(f, name))
            else:
                raise e
        elif magic[:len(ImageBackup.NTFSCLONE)] == ImageBackup.PARTCLONE:
            if isRegularFile(file):
                file.seek(0)
                return readImage(file, sequential, name,
                                 lambda f:PartClone(f, name))
            else:
                raise e
        elif len(magic) >= 2:
            # Uncompress on the fly if we are only going to read
            # the image sequentially.
            word = struct.unpack('<H', magic[:2])[0]
            if word == ImageBackup.GZIP:
                if not sequential:
                    raise WrongImageFile(compressedMsg(name, 'gz'), magic)
                file.seek(0)
                gzip_file = gzip.open(filename=file, mode='rb')
                return readImage(gzip_file, sequential, name, fn)
            elif word == ImageBackup.BZIP2:
                if not sequential:
                    raise WrongImageFile(compressedMsg(name, 'bz2'), magic)
                file.seek(0)
                bz2_file = bz2.open(filename=file, mode='rb')
                return readImage(bz2_file, sequential, name, fn)
            elif word == ImageBackup.ZSTD:
                if not sequential:
                    raise WrongImageFile(compressedMsg(name, 'zstd'), magic)
                file.seek(0)
                zstd_file = pyzstd.ZstdFile(filename=name, mode='rb')
                return readImage(zstd_file, sequential, name, fn)
            elif word == ImageBackup.XZ:
                raise WrongImageFile(compressedMsg(name, 'xz'), magic)
            elif word == ImageBackup.LZMA:
                raise WrongImageFile(compressedMsg(name, 'lzma'), magic)
            elif word == ImageBackup.LZ4:
                raise WrongImageFile(compressedMsg(name, 'lz4'), magic)
            else:
                raise e
        else:
            raise e

def main():
    """
    Processes command-line argumments, reads image and mounts it as
    virtual partition.
    """

    parser = argparse.ArgumentParser(prog='vntfsclone',
                                     description='Mount ntfsclone image '
                                     'backup as virtual partition.')
    parser.add_argument('image', type=argparse.FileType('rb'),
                        help='partclone image to read')
    parser.add_argument('-m', '--mountpoint', type=isEmptyDirectory,
                        help='mount point for virtual partition; '
                        'an empty directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='dump header and bitmap info')
    parser.add_argument('-c', '--crc_check', action='store_true',
                        help='read the entire image (slow!)')
    parser.add_argument('-d', '--debug_fuse', action='store_true',
                        help='enable FUSE filesystem debug messages')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='suppress progress bar when indexing')
    args = parser.parse_args()

    try:

        image = readImage(args.image, args.mountpoint is None, args.image.name,
                          lambda f:NtfsClone(f, args.image.name))

        if args.verbose:
            print(image)
            print()

        if args.mountpoint is not None:

            image.buildBlockIndex(progress_bar=not args.quiet)

            try:

                runFuse(image, args.mountpoint, args.debug_fuse)

            except Exception as e:
                print(file=sys.stderr)
                print(f'FUSE file system errored out with: "{e}".',
                      file=sys.stderr)
                sys.exit(1)

        elif args.crc_check:
            print("CRC-Check requested; ntfsclone images do not have CRC's - "
                  "reading entire image.")
            image.blockReader(progress_bar=not args.quiet, verify_crc=True)


    except ImageBackupException as e:
        print(file=sys.stderr)
        print('Error:', e, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
