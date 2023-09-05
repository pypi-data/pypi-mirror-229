#!/usr/bin/env python3
import argparse, bz2, gzip, io, os, struct, sys
from typing import Callable

from .imagebackup import ImageBackupException, WrongImageFile, ImageBackup
from .partclone import PartClone
from .ntfsclone import NtfsClone, readImage
from .fuse import runFuse, isEmptyDirectory

def indexSizeType(arg: str) -> int:
    "Is argument an acceptable argument for option --index_size?"
    try:
        iarg = int(arg)
    except:
        raise argparse.ArgumentTypeError(f"'{arg}' is not an integer")

    if iarg < 1000:
        raise argparse.ArgumentTypeError(f"'{arg}' is too small, "
                                         "should be >= 1000")
    if iarg % 8 != 0:
        raise argparse.ArgumentTypeError(f"'{arg}' is not a multiple of 8")
    return iarg

def main():
    """
    Processes command-line argumments, reads image and mounts it as
    virtual partition.
    """

    parser = argparse.ArgumentParser(prog='vpartclone',
                                     description='Mount partclone image '
                                     'backup as virtual partition.')
    parser.add_argument('image', type=argparse.FileType('rb'),
                        help='partclone image to read')
    parser.add_argument('-m', '--mountpoint', type=isEmptyDirectory,
                        help='mount point for virtual partition; '
                        'an empty directory')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='dump header and bitmap info')
    parser.add_argument('-d', '--debug_fuse', action='store_true',
                        help='enable FUSE filesystem debug messages')
    parser.add_argument('-c', '--crc_check', action='store_true',
                        help='verify all checksums in image (slow!)')
    parser.add_argument('-i', '--index_size', type=indexSizeType,
                        help='Size parameter for building bitmap index; leave '
                        'unchanged unless memory usage too high. Increase '
                        'size to reduce memory usage by doubling or '
                        'quadrupling number '
                        f'repeatedly (default {PartClone.BLOCK_OFFSET_SIZE}).',
                        default=PartClone.BLOCK_OFFSET_SIZE)
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='suppress progress bar in crc check')
    args = parser.parse_args()

    try:

        image = readImage(args.image, args.mountpoint is None, args.image.name,
                          lambda f:PartClone(f, args.image.name,
                                             args.index_size))

        if args.verbose:
            print(image)
            print()

        if args.mountpoint is not None:
            image.buildBlockIndex(progress_bar=not args.quiet)

        if args.crc_check:
            print(f"Verifying all checksums of image '{args.image.name}'...")
            image.blockReader(progress_bar=not args.quiet, verify_crc=True)

        if args.mountpoint is not None:

            try:

                runFuse(image, args.mountpoint, args.debug_fuse)

            except Exception as e:
                print(file=sys.stderr)
                print(f'FUSE file system errored out with: "{e}".',
                      file=sys.stderr)
                sys.exit(1)

    except ImageBackupException as e:
        print(file=sys.stderr)
        print('Error:', e, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
