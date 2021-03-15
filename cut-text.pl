#!/usr/bin/env perl
# cut a chunk of text from a file based on start/end cut tags
# usage: text-cut [beginTag endTag] < file.in > file.out
# if only one tag is given it's used for begin/end
# if none given, defaults are below.
$BeginTag=shift;
$EndTag=shift;

#these tags are regexps!
if (defined $BeginTag) {
    unless (defined $EndTag) {
	$EndTag=$BeginTag;
    }
} else {
        $BeginTag="<!--CUT_START-->";
	$EndTag="<!--CUT_END-->";
    }

# print "$BeginTag | $EndTag\n";exit; # debug

while (<>) {
    if (/$BeginTag/) {
	$_=<>; # force read next line in case start/end tags are the same
	while (!/$EndTag/) { 
	    $_=<>; # keep reading without printing
	    unless (defined $_) { last;} # safety in case no closing tag found
	}
	$_=<>; # to avoid printing the end tag
    }
    print;
}
