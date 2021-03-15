#!/usr/bin/env python
"""
Evaluate python expressions at the command line and display the result.

Simple usage examples:

$ pyx pi**2
9.869604401089358

$ pyx 'f"{pi:.4e}"'
3.1416e+00
"""

import sys
from math import *

text = " ".join(sys.argv[1:])
#print(sys.argv[1:])  # dbg
#print(f"IN : <{text}>") # dbg

val = eval(text)
#print(f"OUT: <{val}>")  # dbg
print(val)
