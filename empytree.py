#!/usr/bin/python
# -*- coding: utf-8 -*-

import os						## Operation system interface
import re 						## Regular expressium operations
import sys  					## System-specific parameters and functions
from glob import glob			## Unix style pathname pattern expansion
import fnmatch					## Matches file names
import shutil					##00
import argparse					## Argument parser
import warnings					##
import json						## json is used for reading the config
import string
from StringIO import StringIO
from pdb import set_trace
from pprint import pprint		## Just for testing purposes


## External modules
import eyed3	## eyed3 id3 tag module: http://eyed3.nicfit.net/
eyed3.log.setLevel("ERROR") 	## Avoid getting tons of warnings, turn off if you want to debug.


def make_file_name_valid(file_name):
	valid_chars = "-_.,()[] %s%s" % (string.ascii_letters, string.digits)
	return ''.join(c for c in file_name if c in valid_chars)


## Search for mp3s in the specified input folder in the JSON config
def search_for_mp3s():
	for inputDir in args.input:
		for root, _, filenames in os.walk(inputDir):
			if args.verbose:
				try:
					print "========================================"+root+": "+', '.join(filenames)+"========================================"
				except:
					pass
			for filename in filenames:
				if fnmatch.fnmatch(filename.lower(),'*.mp3'):
					yield root, filename


def move_non_mp3s(old_path,new_path):
	# Old function, not used anymore
	if (old_path==new_path):
		return True
	print "==Moving all non-mp3s=="
	for root, _, filenames in os.walk(old_path):
		for filename in filenames:
			if not fnmatch.fnmatch(filename.lower(),'*.mp3'):
				print root, filename,"should be moved to",new_path
				# yield root, filename
	return True


def artist_or_va(artist,album_artist):
	if (artist == album_artist):
		return artist
	else:
		return "VA"


def validate_id3_tags(tag):
	if not tag:
		return False
	
	if (tag.artist is None) or (len(tag.artist) == 0):
		try:
			warnings.warn("Could not find artist tag. Skipping file: "+file_name_with_path, Warning)
		except:
			pass
		return False
	
	if (tag.album is None) or (len(tag.album) == 0):
		try:
			warnings.warn("Could not find album tag. Skipping file: "+file_name_with_path, Warning)
		except:
			pass
		return False
	
	if (tag.title is None) or (len(tag.title) == 0):
		try:
			warnings.warn("Could not find title tag. Skipping file: "+file_name_with_path, Warning)
		except:
			pass
		return False
	
	if (tag.track_num is None) or (len(tag.track_num) == 0):
		try:
			warnings.warn("Could not find track number tag. Skipping file: "+file_name_with_path, Warning)
		except:
			pass
		return False
	
	return True


def get_new_root_and_file_name(tag):
	if tag == False:
		return False

	artist = tag.artist
	artist_no_the = tag.artist if not tag.artist.lower().startswith('the ') else tag.artist[4:]
	artist_append_the = tag.artist if not tag.artist.lower().startswith('the ') else tag.artist[4:]+", The"
	artist_first_letter = artist_no_the[0] if artist_no_the[0] not in ["0","1","2","3","4","5","6","7","8","9","!"] else "0-9"
	album_artist = tag.album_artist
	artist_or_va = artist if artist == album_artist else "VA"
	album = tag.album
	disc_num = str(tag.disc_num[0]) if tag.disc_num[0] is not None else ""
	disc_num_2 = str(tag.disc_num[0]).zfill(2) if tag.disc_num[0] is not None else ""
	title = tag.title
	track_num = str(tag.track_num[0]) if tag.track_num[0] is not None else ""
	track_num_2 = track_num.zfill(2)
	year = str(tag.getBestDate())[0:4]
	format_to_use = "ArtistFormat" if (artist == album_artist or album_artist == "") else "VAFormat"

	new_path = args.output
	for level,L in enumerate(data[format_to_use]):
		file_name_level = len(data[format_to_use])-1
		Lformat = L["format"] % locals()
		Luc = L["uppercase"]
		Llc = L["lowercase"]
		Lrs = L["replaceSpaces"]

		if Llc and not Luc:
			# Change to lowercase
			Lformat = Lformat.lower()
		elif Luc and not Llc:
			# Change to uppercase
			Lformat = Lformat.upper()
		
		if Lrs:
			Lformat = Lformat.replace(' ','_')
		
		# Replace characters specified in the JSON
		for key, value in data["ReplaceCharacters"].iteritems():
			Lformat = Lformat.replace(key,value)
		
		Lformat = make_file_name_valid(Lformat)

		if level == file_name_level:
			new_root = new_path
			Lformat += '.mp3'
			# Create the directories we need if we're not in test mode
			if not args.test:
				if not os.path.exists(new_path):
					os.makedirs(new_path)
			new_file_name = Lformat
			return new_file_name, new_root

		new_path = os.path.join(new_path,Lformat)

	return new_file_name, new_root


## Usage:  get_tag(file_name_with_path)
## Before: Full path to a file to get ID3 tag from.
## After:  If the file can be successfully read, return the tag for the file,
##         otherwise return False.
def getTag(file_name_with_path):
	# Let's try to read the file
	try:
		audiofile = eyed3.load(file_name_with_path)
		if not audiofile:
			raise Exception("No audiofile read.")
		return audiofile.tag
	except:
		try:
			warnings.warn("Error reading file with filename: "+file_name+". Skipping file.", Warning)
		except:
			pass
		return False

	# Check if the tags are valid
	if not validate_id3_tags(audiofile.tag):
		try:
			warnings.warn("Missing tag information from file with filename: "+file_name+". Skipping file.", Warning)
		except:
			pass
		return False

	# All is good, return the tag
	return tag

## Usage:  move_to_correct_path(root,file_name)
## Before: The root (directory) of the file to be moved, file_name must be a existing
##         file in the root folder.
## After:  Return 1 if the file was not moved and 0 if it was successfully moved.
def move_to_correct_path(root,file_name):
	global d
	# Join the paths together
	file_name_with_path = os.path.join(root,file_name)
	new_path, new_root = get_new_root_and_file_name(getTag(file_name_with_path))
	
	if new_path == False:
		return 1

	# No need to move the files if the path is the same as before
	if (file_name_with_path==new_path):
		# if args.verbose:
		# 	print file_name_with_path+" is the same as the original path."
		return 1

	if root != new_root:
		# If didn't change we dont have to do anything here
		print "Root has changed", root, new_root
		print "Is root in d?", root in d
		
		if root in d:
			print "d[root] =", d[root]
		
		if root not in d:
			# The folder is not in the dictionary, let's add it
			print "Case 1: root not in d"
			if root in d:
				print d[root]
			d[root] = new_root
		elif d[root] != new_root:
			# Some other file in the folder disagrees which folder they should move to,
			# therefore we decide to not move the folder
			print "Case 2: d[root] not the same as new_root"
			d[root] = False

	if args.test:
		try:
			print file_name,
		except:
			# This happens if python can't convert the unicode string to the output.
			print "???",
		print '->',
		try:
			print new_path
		except:
			# This happens if python can't convert the unicode string to the output.
			print "???"
	else:
		if args.verbose:
			print file_name_with_path, new_path

		shutil.move(file_name_with_path, new_path)
		if args.verbose:
			print "Moved "+file_name+" to "+new_path

		## TODO: Send all other files in the previous folder with the other files
		## TODO: Delete the previous folder(s) (if it's empty?)
		## TODO: Change the tags (e.g. make first letter capital)

	return 0


## The Main function
if __name__ == '__main__':
	# Create a argument parser
	parser = argparse.ArgumentParser(description='Empytree organizes MP3s using ID3 tags.')

	## Hint: add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
	parser.add_argument('--verbose','-v',action='store_true')
	parser.add_argument('--test','-t',action='store_true')
	parser.add_argument('--config','-c',default='config.json',help='Location of the config.json file',action='store')

	args = parser.parse_args()
	
	json_data = open(args.config,'r')
	global data
	data = json.load(json_data)
	# pprint(data)
	json_data.close()
	# if args.input == '':
	args.input = data["Folders"]["input"]
	# if args.output =='':
	args.output = data["Folders"]["output"]
	# except:
	# 	warnings.warn("Could not use config: '"+args.config+"'. Either the config was not found or not valid. Using default options.", Warning)
	# 	print sys.exc_info()[0]

	# args.input = unicode(args.input)
	args.output = unicode(args.output)

	# Print out which arguments are defined as what
	if args.verbose:
		print "Empytree starting..."
		print "========= Arguments ========="
		print "Verbosity is on!"
		print "Running on test mode?",args.test
		# print "Input directory is: "+args.input
		print "Output directory is: "+args.output
		print "============================="

	d = {}
	files_moved = 0
	for root,mp3file in search_for_mp3s():
		# try:
		# 	if args.verbose:
		# 		print "Trying to move file "+mp3file
		# except:
		# 	pass
		if not move_to_correct_path(root,mp3file):
			files_moved += 1

	if args.verbose:
		print "Empytree finished successfully! Total files moved:",files_moved

	if args.verbose:
		print d