#!/usr/bin/env python

# Copies jpegs from source to destination while renaming based on EXIF
# timestamp
#
# Copyright (c) 2009 William Ting (william dot h dot ting at gmail dot com)
# All rights reserved
# Site: https://sourceforge.net/projects/exifedit
# SVN: svn co https://exifedit.svn.sourceforge.net/svnroot/exifedit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import imghdr
import mimetypes
import optparse
import os
import sys
import time
import EXIF
import cPickle
import shutil

VERSION = "0.1.2"

class TimeError(Exception) :
	def __init__(self, value) :
		self.parameter = value
	def __str__(self) :
		return repr(self.parameter)

def set_options() :
	"""
	Parses command line options, checks source directory existence.
	"""
	global OPT, ARG, SOURCE, DEST
	usage="%prog [OPTION] SOURCE DEST"
	version="%prog " + VERSION
	description="Copies jpeg and raw files with the same name within SOURCE to DEST, renaming the file based on the EXIF timestamp."
	parser = optparse.OptionParser(usage=usage,version=version,description=description)

	parser.set_defaults(original=False,raw=True,strip=0)

	parser.add_option("-d", "--duplicate",
		dest="duplicate", action="store_false",
		help="Check for duplicates. (unfinished)")
	parser.add_option("-n", "--dry-run",
		dest="dry-run", action="store_false",
		help="Simulate actions without making any changes. (unfinished)")
	parser.add_option("-t", "--template",
		dest="template",
		help="Change destination directory and file format, default: YYYY/MM/DD/YYYY-MM-DD_HH24.MI.SS (unfinished)")
	parser.add_option("-q", "--quiet",
		dest="verbose", action="store_false",
		help="Suppress all output. (unfinished)")
	parser.add_option("-v", "--verbose",
		dest="verbose", action="store_true",
		help="Verbosely list files processed.")
	parser.add_option("-w", "--raw",
		dest="raw", action="store_true",
		help="Performs same actions on raw files with the same filename. [default] (unfinished)")
	parser.add_option("-W", "--noraw",
		dest="raw", action="store_false",
		help="Do not perform same actions on raw files with the same filename. (unfinished)")

	(OPT, ARG) = parser.parse_args()

	#checks for SOURCE and DEST arguments
	if len(ARG) == 1 and OPT.original == False :
		parser.error("The option --original (modifies the source files) must be specified when using only a source directory.")
	elif len(ARG) < 2 and OPT.original == False :
		parser.print_help()
		sys.exit(2)

	#check for SOURCE
	SOURCE = ARG[0]
	DEST = ARG[1]
	if not os.path.exists(SOURCE) :
		print "ERROR: SOURCE directory does not exist."
		sys.exit(2)

def rename_photos() :
	"""
	Traverses through source directory, checks for valid jpeg, extracts EXIF timestamp,
	checks for existing file, creates YYYY/MM/DD dir hieararchy, copies to destination folder.
	"""
	global OPT, DEST

	for dir_path, dir_names, file_names in os.walk(SOURCE) :
		for file in file_names :
			if mimetypes.guess_type(file)[0] == 'image/jpeg' :
				if imghdr.what(os.path.join(dir_path,file)) == 'jpeg' :
					if OPT.verbose :
						print "*PROCESS:", os.path.join(dir_path,file)
					try :
						tmp = exif_get_datetime(os.path.join(dir_path,file))
					except TimeError, (e):
						print "ERROR: Timestamp [", e.parameter, "] -", os.path.join(dir_path,file)
						continue
					dest_dir = os.path.join(DEST+time.strftime("%Y"+os.sep+"%m"+os.sep+"%d",tmp[0]))
					mk_dir(dest_dir)
					dest_filename = tmp[1]
					if os.path.isfile(os.path.join(dest_dir, dest_filename+".jpg")) :
						found_name = False
						postfix = 1
						while not found_name :
							if not os.path.isfile(os.path.join(dest_dir, dest_filename+"_"+str(postfix)+".jpg")) :
								dest_filename = dest_filename + "_" + str(postfix)
								found_name = True
							else :
								postfix += 1
					shutil.copy2(os.path.join(dir_path,file),os.path.join(dest_dir, dest_filename+".jpg"))
					print "COPY:", os.path.join(dir_path,file), "==>",os.path.join(dest_dir, dest_filename+".jpg")
				else :
					print "ERROR: Corrupt File -", os.path.join(dir_path,file)


def exif_get_datetime(file, format = None):
	"""Extracts and parses DateTimeOriginal from the image and if no optional format is
	passed then returns the default format.  Otherwise it converts into a struct_time and
	is formatted with the optional parameter.
	"""
	global OPT

	#retrieve "EXIF DateTimeOriginal" tag
	f = open(file, 'rb')
	tags = EXIF.process_file(f, details=False, stop_tag='DateTimeOriginal')
	f.close()

	#converts instance into string and splits it
	try :
		str = cPickle.dumps(tags['EXIF DateTimeOriginal']).split()
		#if OPT.verbose :
			#print "TIMESTAMP:",str
		d = str[9][2:] #grabs the date
		t = str[10][:-1] #grabs the time

		if d == "0000:00:00" :
			raise TimeError((d,t))

		#converts time into a struct_time, always assume tm_isdst=-1
		t_str = time.strptime(d + " " + t,"%Y:%m:%d %H:%M:%S")
		if format == None :
			return (t_str,time.strftime("%Y-%m-%d_%H.%M.%S",t_str))
		else :
			return (t_str,time.strftime(format,t_str))
	except KeyError: #for missing timestamp tags
		raise TimeError(None)

def mk_dir(path) :
	"""
	Encapsulating os.makedirs within a try/catch block.
	"""
	if not os.path.exists(path):
		try :
			os.makedirs(path)
		except OSError :
			print "ERROR: Unable to create directory:",path
			sys.exit(1)

if __name__ == "__main__" :
	set_options()
	rename_photos()
	sys.exit(0)
