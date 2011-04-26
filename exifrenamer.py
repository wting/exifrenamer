#!/usr/bin/env python

# Copies images from source to destination while renaming based on EXIF
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

#todo:

import imghdr
import mimetypes
import optparse
import os
import sys
import time
import cPickle
import shutil
import hashlib

#included with package, otherwise located at
#https://sourceforge.net/projects/exif-py/
import EXIF

VERSION = "0.1.23"
IMAGES = []

class TimeError(Exception):
	def __init__(self, value):
		self.parameter = value
	def __str__(self):
		return repr(self.parameter)

def set_options():
	"""
	Parses command line options, checks source directory existence.
	"""
	global OPT, ARG, SOURCE, DEST, FORMAT_DIR, FORMAT_FILE
	usage="%prog [OPTION] SOURCE DEST"
	version="%prog " + VERSION
	description="Copies jpeg and raw files with the same name within SOURCE to DEST, renaming the file based on the EXIF timestamp."
	parser = optparse.OptionParser(usage=usage,version=version,description=description)

	parser.set_defaults(original=False,move=True,raw=True,run=True,template=None,verbose=1)

	parser.add_option("-n", "--dry-run",
		dest="run", action="store_false",
		help="Simulate actions without making any changes.")
	parser.add_option("-c", "--copy",
		dest="move",action="store_false",
		help="Copy the original file as opposed to moving.")
	parser.add_option("-t", "--template",
		dest="template",
		help="Change destination directory and file format, default example: YYYY/MM/YYYYMMDD/YYYY-MM-DD_24hr\
				%Y = 4 digit year, %y = 2 digit year, %m = 2 digit month, %b = abbreviated month name, %B = full month name, %d = 2 digit day,\
				%H = 24 hour clock, %I = 12 hour clock, %M = minutes, %S = seconds")
	parser.add_option("-q", "--quiet",
		dest="verbose", action="store_const", const=0,
		help="Suppress all output.")
	parser.add_option("-v", "--verbose",
		dest="verbose", action="store_const", const=2,
		help="Verbosely list files processed.")
	parser.add_option("-w", "--noraw",
		dest="raw", action="store_false",
		help="Do not perform same actions on raw files with the same filename.")

	(OPT, ARG) = parser.parse_args()

	#checks for SOURCE and DEST arguments
	if len(ARG) == 1 and OPT.original == False:
		#parser.error("The option --original (modifies the source files) must be specified when using only a source directory.")
		print "No DEST directory specified, using default directory ./ExifRenamer-YYYYMMDD_HH-MM-SS/"
		DEST = "ExifRenamer-" + time.strftime("%Y%m%d_%H-%M-%S", time.localtime()) + os.sep
	elif len(ARG) < 2 and OPT.original == False:
		parser.print_help()
		sys.exit(2)
	else:
		DEST = ARG[1]

	#check for SOURCE
	SOURCE = ARG[0]
	if not os.path.exists(SOURCE):
		print "ERROR: SOURCE directory does not exist."
		sys.exit(2)

	#parse template format
	if OPT.template == None:	#/2011/03/20110311/
		FORMAT_DIR = "%Y"+os.sep+"%m"+os.sep+"%Y%m%d"
		FORMAT_FILE = "%Y-%m-%d_%H.%M.%S"
	else:
		if OPT.verbose > 1:
			print "*TEMPLATE:",OPT.template
		if OPT.template.find(os.sep) == -1:
			print "ERROR: Invalid template, DEST cannot be current directory."
			sys.exit(2)
		format = OPT.template.replace("/",os.sep)
		format = OPT.template.replace("\\",os.sep)
		format = format.rpartition(os.sep)
		FORMAT_DIR = format[0]
		FORMAT_FILE = format[2]

def build_list():
	"""
	Traverses through source directory, checks for valid jpeg, extracts EXIF timestamp,
	checks for existing file, creates YYYY/MM/DD dir hieararchy, copies to destination folder.
	"""
	global IMAGES,SOURCE

	if OPT.verbose >= 1:
		print "Building file list",
	cnt = 0
	for dir_path, dir_names, file_names in os.walk(SOURCE):
		for file in file_names:
			if OPT.verbose > 1:
				print file
			#finds jpegs based on mimetype and image headers
			if mimetypes.guess_type(file)[0] == 'image/jpeg' and imghdr.what(os.path.join(dir_path,file)) == 'jpeg':
				IMAGES.append((dir_path,file))
				if OPT.verbose >= 1:
					if cnt % 100 == 0:
						print ".",
				cnt += 1
			elif OPT.verbose > 1:
				if mimetypes.guess_type(file)[0] != 'image/jpeg':
					print "\t--> fail jpeg mime type"
				if imghdr.what(os.path.join(dir_path,file)) != 'jpeg':
					print "\t--> fail jpeg image header"
	print "\n",len(IMAGES),"images to consider."

def process_list():
	"""
	Traverses the list and copies/moves it to the destination.
	"""
	global OPT, DEST, FORMAT_FILE, IMAGES
	error = []

	#list from: http://en.wikipedia.org/wiki/Raw_image_format
	raw_exts = [".raf",".crw",".cr2",".tif",".mrw",".nef",".nrw",".orf",".dng",".ptx",".pex",".arw",".srf",".sr2",".raw",".rw2"]
	index = 1
	for source_dir, source_file in IMAGES:
		count = "[" + str(index) + "/" + str(len(IMAGES)) + "]"
		index += 1
		source = os.path.join(source_dir,source_file)
		source_base = os.path.splitext(source)[0]

		#handle bad timestamps within jpegs
		try:
			if OPT.verbose > 1:
				print "*PROCESS",count,":",source
			tmp = exif_get_datetime(source)
		except TimeError, (e):
			print "ERROR",count,":",source,"\n\t--> invalid timestamp:", e.parameter
			error.append(source + "\n\t--> invalid timestamp:" + e.parameter)
			continue

		dest_dir = os.path.join(DEST+time.strftime(FORMAT_DIR,tmp[0]))
		mk_dir(dest_dir)
		dest = os.path.join(dest_dir,tmp[1]+".jpg")
		dest_base = os.path.splitext(dest)[0]

		#check for collisions/duplicates
		skip_name = ""
		found_name = False
		if os.path.isfile(dest):
			if md5sum(source) == md5sum(dest):
				found_name = True
				skip_name = dest
			postfix = 1
			while not found_name:
				if os.path.isfile(dest_base+"_"+str(postfix)+".jpg"):
					if md5sum(source) == md5sum(dest_base+"_"+str(postfix)+".jpg"):
						found_name = True
						skip_name = dest
				elif not os.path.isfile(dest_base+"_"+str(postfix)+".jpg"):
					dest_base += "_" + str(postfix)
					dest = dest_base + ".jpg"
					found_name = True
				postfix += 1

		if skip_name != "":
			print "SKIP",count,":",source,"\n\t--> exists at destination:",skip_name
		else:
			#find raw files
			raw_ext = ""  #assumes one raw file per jpg
			if OPT.raw:
				for ext in raw_exts:
					if os.path.isfile(source_base+ext):
						raw_ext = ext
					elif os.path.isfile(source_base+ext.upper()):
						raw_ext = ext.upper()

			if OPT.run:
				if not OPT.move:
					shutil.copy2(source,dest)
					if OPT.raw and raw_ext != "":
						shutil.copy2(source_base+raw_ext,dest_base+raw_ext)
				else:
					shutil.move(source,dest)
					if OPT.raw and raw_ext != "":
						shutil.move(source_base+raw_ext,dest_base+raw_ext)
				#to change modify timestamp on files to match exif data
				#os.utime(dest,(atime,mtime))
				#if OPT.raw and raw_ext != "":
					#os.utime(dest_base+raw_ext)

			if OPT.verbose >= 1:
				if not OPT.move:
					print "COPY",count,":",source,"\n\t-->",dest
					if OPT.raw and raw_ext != "":
						print "COPY",count,":",source_base+raw_ext,"\n\t-->",dest_base+raw_ext
				else:
					print "MOVE",count,":",source,"\n\t-->",dest
					if OPT.raw and raw_ext != "":
						print "MOVE",count,":",source_base+raw_ext,"\n\t-->",dest_base+raw_ext

	#closure
	if len(error) != 0:
		print "\n____________________________________________________________________\n\nErrors encountered"
		for e in error:
			print e

def exif_get_datetime(file):
	"""
	Extracts and parses DateTimeOriginal from the image and if no optional format is
	passed then returns the default format.  Otherwise it converts into a struct_time and
	is formatted with the optional parameter.
	"""
	global OPT, FORMAT_FILE

	#retrieve "EXIF DateTimeOriginal" tag
	f = open(file, 'rb')
	tags = EXIF.process_file(f, details=False, stop_tag='DateTimeOriginal')
	f.close()

	#converts instance into string and splits it
	try:
		str = cPickle.dumps(tags['EXIF DateTimeOriginal']).split()
		d = str[9][2:] #grabs the date
		t = str[10][:-1] #grabs the time

		#handles malformed timestamps
		if OPT.verbose > 1:
			print "TIMESTAMP:",d,t
		if d == "0000:00:00":
			raise TimeError(d)

		#converts time into a struct_time, always assume tm_isdst=-1
		t_str = time.strptime(d + " " + t,"%Y:%m:%d %H:%M:%S")
		return (t_str,time.strftime(FORMAT_FILE,t_str))
	except KeyError: #handles missing timestamps
		raise TimeError("missing")
	except ValueError: #handles malformed timestamps
		raise TimeError("malformed")

def md5sum(fname):
	"""
	Returns the md5sum of a filename.
	"""
	global OPT
	try:
		if OPT.verbose > 1:
			print "*MD5SUM:", fname,
		f = file(fname,'rb')
	except:
		return None ##cannot open file

	m = hashlib.md5()
	while True:
		d = f.read(8096)
		if not d:
			break
		m.update(d)

	if OPT.verbose > 1:
		print "=",m.hexdigest()
	return m.hexdigest()

def mk_dir(path):
	"""
	Encapsulating os.makedirs within a try/catch block.
	"""
	global OPT

	if not os.path.exists(path):
		try:
			if OPT.run:
				os.makedirs(path)
		except OSError:
			print "ERROR: Unable to create directory:",path
			sys.exit(1)

if __name__ == "__main__":
	set_options()
	build_list()
	process_list()
	#rename_photos()

	if not OPT.run:
		print "DRY RUN: All actions simulated."
	sys.exit(0)