#!/usr/bin/env python
"""Retrieve pictures taken with a Canon camera from a CF card.

    %prog [options]
"""

from __future__ import with_statement


# Global constants
DEST_DIR = '$HOME/media/photo/digicam'

CD_NAMES = ['CANON_DC', 'EOS_DIGITAL', 'POWERSHOT', 'NO NAME', 'LUMIX',
            'sda1', 'sdb1', 'sdc1', 'disk', 'dcim']

prefixes = ['/Volumes', '/media/fperez']

CARD_DIRS = [pfx + '/' + name for pfx in prefixes for name in CD_NAMES]

KNOWN_EXT = set(['.jpg', '.avi', '.mov', '.thm', '.cr2', '.mp4', '.rw2'])


# needed modules
import os
import platform
import re
import shutil
import time

from optparse import OptionParser


# code begins
xsys = os.system


def shexp(s):
    "Expand $VARS and ~names in a string, like a shell"
    return os.path.expandvars(os.path.expanduser(s))



def parse_args():
    "Parse command line and return opts,args"

    parser = OptionParser(usage=__doc__)
    newopt = parser.add_option

    newopt('-c', '--card_dir', default=CARD_DIRS[0],
           help='CF card directory')
    newopt('-D', '--dest_dir', default=shexp(DEST_DIR),
           help='Destination directory base')
    newopt('-g', '--gthumb', action='store_true', default=False,
           help='Open gthumb with the destination directory')
    newopt('-d', '--delete', action='store_true', default=False,
           help='Delete the original pictures from the CF card')
    newopt('-a', '--already', type=int, default=None,
           help='Maximum numeric ID of images already copied ' +
                '(nothing with an ID lower or equal to this will '
                'be copied again)')

    return parser.parse_args()


def make_dest_dir(base):
    """Make the name of the destination directory.

    Interactively queries for the new dir, which is appended to the base.  By
    default, a timestamp is used as a prefix, but this can be overridden if the
    user enters a destination starting with '/'."""

    prefix = time.strftime("%y%m%d-")

    print('Base dir:', base)
    newprefix = input('Enter new destination [%s]: ' % prefix)
    if not newprefix:
        newprefix = prefix
    elif newprefix.startswith('/'):
        newprefix = newprefix[1:]
    else:
        newprefix = prefix + newprefix
    return os.path.join(base, newprefix)


def process_raw(dirname, ext='.rw2'):
    """Process a directory for any raw files of the given extension.

    - Writes a manifest.txt file with all the jpg files that have a matching
    raw file

    - Moves all raw files to a 'raw' subdir.

    Returns
    -------
      Number of raw files moved.
    """

    from glob import glob
    # first, find if there are any raw files in dir
    raw_files = glob(dirname+'/*%s' % ext)
    if not raw_files:
        return 0

    # If we do find raw files, leave a manifest of the matching jpgs.  We want
    # to find the set of files that have both a jpg and a raw file, and then
    # write them out as a list into a manifest file (the jpgs).  Then, one can
    # just browse through the jpgs and delete the unwanted ones, and based on
    # the manifest, remove the matching raw files
    jpg_files = glob(dirname+'/*.jpg')

    raw_bases = set(os.path.splitext(f)[0] for f in raw_files)
    jpg_bases = set(os.path.splitext(f)[0] for f in jpg_files)
    common = raw_bases.intersection(jpg_bases)
    common_jpg = sorted([f+'.jpg' for f in common])

    with open(dirname + '/manifest.txt', 'w') as manifest:
        for f in common_jpg:
            manifest.write(os.path.split(f)[-1]+'\n')

    # Finally,  make a raw subdir and move all the raw files there
    raw_dir = dirname+'/raw'
    if not os.path.isdir(raw_dir):
        os.mkdir(raw_dir)

    # Move raw files to final destination and remove executable bit
    xsys('mv %s %s' % (' '.join(raw_files), raw_dir))
    xsys('chmod -x %s/*%s' % (raw_dir, ext))

    return len(raw_files)


def main():
    """Copy/move files from the CF card to the given destination.

    This script has zero error control, and works with hard-coded assumptions
    about the layout of Canon's filesystem on the CF card."""

    opts, args = parse_args()

    for card_dir in [opts.card_dir] + CARD_DIRS:
        if os.path.isdir(card_dir):
            break
    else:
        raise RuntimeError('CF Card directory not found')

    # extract a few options as locals for speed/convenience
    dest_dir = make_dest_dir(opts.dest_dir)

    data_dir = card_dir+'/dcim'
    if not os.path.isdir(data_dir):
        data_dir = card_dir+'/DCIM'

    if opts.delete:
        file_op = shutil.move
        op_name = 'Moving'
    else:
        file_op = shutil.copy2
        op_name = 'Copying'

    print('Destination directory:', dest_dir)
    tot_files = 0  # counter to report at the end

    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    digits_re = re.compile(r'[^\d]*(\d+)[^\d]*')

    for dirpath, dirnames, all_filenames in os.walk(data_dir):
        #print('dp:', dirpath)  # dbg
        ## if not dirpath.lower().endswith('canon'):
        ##     # All Canon image directories have names of the form NNNcanon,
        ##     # where NNN are three digits.  The rest contain meta-data we won't
        ##     # copy (the image catalogs).
        ##     print('Skipping:', dirpath)  # dbg
        ##     continue

        # Filter filenames first
        filenames = [f for f in all_filenames
                     if os.path.splitext(f)[1].lower() in KNOWN_EXT]

        if opts.already is not None:
            # Copy only images with a numeric identifier higher than that of
            # images that have been already downloaded
            to_copy = []
            for f in filenames:
                match = digits_re.match(f)
                if not match or int(match.group(1)) > opts.already:
                        to_copy.append(f)
            filenames = to_copy

        nfiles = len(filenames)
        tot_files += nfiles
        #print('Files to copy:', filenames) # dbg

        print('%s <%s> files from <%s>' % (op_name, nfiles, dirpath))
        for f in filenames:
            file_op('%s/%s' % (dirpath, f),
                    '%s/%s' % (dest_dir, f.lower()))

    print()
    print('A total of <%s> files were transferred' % tot_files)

    nraw = process_raw(dest_dir)
    if nraw:
        print('  and a total of <%s> RAW files were moved to raw subdir.'
              % nraw)

    # mode cleanup, since by default FAT32 filesystems under linux mount with
    # the execute bit on for all files
    exts = ' '.join([f'{dest_dir}/*'+e for e in KNOWN_EXT])
    xsys(f'chmod -x {exts}')
    
    # unmount card before exiting
    umount = 'diskutil umount' if platform.system() == 'Darwin' else 'umount'
    xsys(f'sync && {umount} {card_dir}')

    # Open destination directory
    if opts.gthumb:
        xsys('gthumb %s &' % dest_dir)
    xsys(f'open {dest_dir}')


if __name__ == '__main__':
    main()
