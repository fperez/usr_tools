#!/usr/bin/env python
"""
Show all authors of git repos in a list of directories.

Calls `git shortlog -sn` on all input directories and combines the output
into a single set of unique results.

Usage:

   authors.py dir1 dir2 ...
"""

import subprocess
import sys

from pathlib import Path


CMD = "git --git-dir %s shortlog -sn | awk '{$1=\"\"; print $0}'"


dirs = sys.argv[1:]
print(f'Directories to check: {dirs}')
authors = set()
repos = 0
for d in dirs:
    repo = Path(d)/'.git'
    if not repo.is_dir():
        print('--- Skipping dir:', d)
        continue
    print('+++ Checking dir:', d)
    authors.update(subprocess.getoutput(CMD % repo).splitlines())
    repos += 1

print(f'\nAuthors:\n{sorted(authors)}\n')
print('Total:', len(authors), 'authors in', repos, 'repositories.')
