#!/usr/bin/env python
"""Extract the part of a Latex document between (but excluding) the begin/end
document tags.  This allows easy inclusion of that text into other lyx/latex
files.

Usage:

textract.py filename.

WARNING: It modifies IN PLACE the input given file if the INPLACE flag below
is set. Otherwise it prints to stdout."""

INPLACE = True

import os, sys, tempfile
fname = sys.argv[1]

if INPLACE:
    outfname = tempfile.mktemp()
    outfile = file(outfname,'w')
else:
    outfile = sys.stdout

fiter = file(fname)
for line in fiter:
    if line.startswith("\\begin{document}"):
        while 1:
            try:
                line = fiter.next()
            except StopIteration:
                break
            else:
                if line.startswith("\end{document}"):
                    break
                else:
                    print >> outfile, line,
if INPLACE:
    print "WARNING: modifying file <%s> in place.  Backup left in <%s~>" % \
          (fname,fname)
    outfile.close()
    # Use 'mv' instead of os.rename() b/c os.rename fails across filesystems.
    os.system("mv %s %s" % (fname,fname+'~'))
    os.system("mv %s %s" % (outfname,fname))
