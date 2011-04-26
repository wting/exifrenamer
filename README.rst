========
EXIFRENAMER
========

----------------------------
Moving files based on EXIF timestamps
----------------------------

I wrote this small utility to alleviate the issue of manually organizing your photos or getting rid of DSCN_0012.JPG filenames.

The utility reads the EXIF timestamp from the image file and then moves it to a destination directory based on that data.

Currently matches against the following file extensions:
- .jpg
- .tif
- .dng
- .nef
- .crw
- .cr2
- .raw
- .raf
- .mrw
- .orf
- .ptx
- .pex
- .arw
- .srf
- .sr2
- .rw2

Requires python to be installed and supports Linux and Cygwin bash shells.

Examples
========

::

 exifrenamer.py ~/inbox/ ~/outbox/

will give an example out of::
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


Author
======

William Ting (i.am at williamting.com)

License
=======

exifrenamer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

exifrenamer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with exifrenamer.  If not, see <http://www.gnu.org/licenses/>.

Installation
============

Grab a copy of the source with::
 git clone git://github.com/wting/exifrenamer.git

Then either add the directory to your path or sym link it from /usr/local/bin/.

Uninstallation
==============

Simple remove the source code directory and sym link /usr/local/bin/exifrenamer.py if it exists.
