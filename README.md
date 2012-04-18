NAME
----

exifrenamer - move photos based on timestamp metadata

SYNOPSIS
--------

exifrenamer is a small program designed to alleviate the issue of
manually organizing your photos or getting rid of meaningless filenames
(e.g. DSCN0012.JPG).

The program reads the EXIF timestamp from the image file and then moves
it to a destination directory based on that data.

Installation
------------

### Requirements

Python v2.7+

Uninstallation
--------------

Delete the program directory:

    rm -fr ~/.exifrenamer/

Remove the following line from your `.bashrc`:

    export PATH=~/.exifrenamer/bin:"${PATH}"

USAGE
-----

Example command to move files from one folder to another:

    exifrenamer.py ~/inbox/ ~/outbox/

Command results:

    Building file list .
    5 images to consider.
    MOVE [1/5] : test_images/01/nikon d60.jpg
            --> outbox/2009/01/20090123/2009-01-23_19.31.31.jpg
    MOVE [2/5] : test_images/01/02/canon 350d.jpg
            --> outbox/2009/01/20090123/2009-01-23_21.37.03.jpg
    ERROR [3/5] : test_images/fail/0000 timestamp.jpg
            --> invalid timestamp: 0000:00:00
    ERROR [4/5] : test_images/fail/notimestamp.jpg
            --> invalid timestamp: missing
    MOVE [5/5] : test_images/raw/dsc_5149.jpg
            --> outbox/2009/03/20090315/2009-03-15_22.07.00.jpg
    MOVE [5/5] : test_images/raw/dsc_5149.nef
            --> outbox/2009/03/20090315/2009-03-15_22.07.00.nef

    ____________________________________________________________________

    Errors encountered
    test_images/fail/0000 timestamp.jpg
            --> invalid timestamp:0000:00:00
    test_images/fail/notimestamp.jpg
            --> invalid timestamp:missing

OPTIONS
-------

Options must be passed to 'exifrenamer' and not the 'j' wrapper
function.

    -a, --add DIR       manually add path to database

    --stat              show database entries and their key weights

    --version           show version information and exit

KNOWN ISSUES
------------

FILES
-----

exifrenamer is installed into the home directory contained in
*\~/.exifrenamer/*.

REPORTING BUGS
--------------

For any issues please visit the following URL:

*https://github.com/wting/exifrenamer/issues*

AUTHORS
-------

exifrenamer written by William Ting.

COPYRIGHT
---------

Copyright © 2012 Free Software Foundation, Inc. License GPLv3+: GNU GPL
version 3 or later <http://gnu.org/licenses/gpl.html>. This is free
software: you are free to change and redistribute it. There is NO
WARRANTY, to the extent permitted by law.
