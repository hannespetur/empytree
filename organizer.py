#!/usr/bin/python
# -*- coding: utf-8 -*-

import re 						## Regular expressium operations
import sys  					## System-specific parameters and functions
import os						## Operation system interface
import fnmatch					## Matches file names
import shutil					## Used for moving files

## Local files
from common import *

## Search for mp3s in the specified input folder in the JSON config
def search_for_mp3s(input_dirs,verbose):
	for input_dir in input_dirs:
		for root, _, filenames in os.walk(input_dir):
			if verbose:
				try:
					print "\n===== "+root+": "+' '.join(filenames)+" ====="
				except:
					pass
			for filename in filenames:
				if fnmatch.fnmatch(filename.lower(),'*.mp3'):
					yield root, filename

## Usage:  s = artist_or_va(artist,album_artist)
## Before: artist is a string with the artist from the ID3 tag, album_artist
##         is the album artist from the ID3 tag.
## After:  If the two strings match or album artist is empty string, return 
##         the artist, otherwise return the string "VA"
def artist_or_va(artist,album_artist):
	if (artist == album_artist or album_artist == "" or album_artist == None):
		return artist
	else:
		return "VA"

## Usage:  new_file_name, new_root = getNewRootAndFilename(tag)
## Before: Tag is a valid ID3 tag or False
## After:  new_file_name is a new file name created from the ID3 tags and new_root is the new root.
def getNewRootAndFilename(tag,file_name,args,data):
	if tag == False or tag == None:
		return False, False

	album = tag.album
	album_artist = tag.album_artist
	artist = tag.artist
	artist_append_the = tag.artist if not tag.artist.lower().startswith('the ') else tag.artist[4:]+", The"
	artist_no_the = tag.artist if not tag.artist.lower().startswith('the ') else tag.artist[4:]
	artist_first_letter = artist_no_the[0] if artist_no_the[0] not in ["0","1","2","3","4","5","6","7","8","9","!"] else "0-9"
	artist_or_va = artist if artist == album_artist else "VA"
	disc_num = str(tag.disc_num[0]) if tag.disc_num[0] is not None else ""
	disc_num_2 = str(tag.disc_num[0]).zfill(2) if tag.disc_num[0] is not None else ""
	title = tag.title
	track_num = str(tag.track_num[0]) if tag.track_num[0] is not None else ""
	track_num_2 = track_num.zfill(2)
	year = str(tag.getBestDate())[0:4] if tag.getBestDate() is not None else "0000"
	format_to_use = "ArtistFormat" if (artist == album_artist or album_artist == "" or album_artist == None) else "VAFormat"

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
			new_file_name = Lformat
			return new_file_name, new_root

		new_path = os.path.join(new_path,Lformat)

	return new_file_name, new_root


## Usage:  rename_files(root,file_name,args,data)
## Before: The root (directory) of the file to be moved, file_name must be a existing
##         file in the root folder.
## After:  Return 1 if the file was not moved and 0 if it was successfully moved.
def rename_files(root,file_name,args,data):
	global d, mismatch
	# Join the paths together
	file_name_with_path = os.path.join(root,file_name)
	tag = getTag(file_name_with_path)
	if tag == False or tag == None:
		return 1

	new_file_name, new_root = getNewRootAndFilename(tag,file_name,args,data)
	if new_file_name == False:
		return 1
	new_path = os.path.join(new_root,new_file_name)
	
	
	if new_path == False:
		return 1

	# No need to move the files if the path is the same as before
	if (file_name_with_path==new_path):
		# if args.verbose:
		# 	print file_name_with_path+" is the same as the original path."
		return 1

	if root != new_root:
		# If didn't change we dont have to do anything here	
		if root not in d:
			# The folder is not in the dictionary, let's add it
			if root in d:
				print d[root]
			d[root] = new_root
		elif d[root] != new_root:
			# Some other file in the folder disagrees which folder they should move to,
			# therefore we decide to not move the folder
			if args.verbose:
				print "Case 2: d[root] not the same as new_root"
			if root not in mismatch:
				mismatch[root] = []
			if d[root] not in mismatch[root] and d[root] != False:
				mismatch[root].append(d[root])
			if new_root not in mismatch[root]:
				mismatch[root].append(new_root)
			if args.verbose:
				print "WARNING:",d[root],"and",new_root
			d[root] = False

	# Change file name
	old_file_name_path = os.path.join(root,file_name)
	new_file_name_path = os.path.join(root,new_file_name)
	if old_file_name_path != new_file_name_path:
		if args.mode == "test":
				try:
					print file_name,
				except:
					# This happens if python can't convert the unicode string to the output.
					print "???",
				print '->',
				try:
					print new_file_name
				except:
					# This happens if python can't convert the unicode string to the output.
					print "???"
		else:
			if args.verbose:
				try:
					print file_name+' -> '+new_file_name
				except:
					pass

			shutil.move(old_file_name_path, new_file_name_path)
			if args.verbose:
				print "Moved "+old_file_name_path+" to "+new_file_name_path
	else:
		return 1
			## TODO: Change the tags (e.g. make first letter capital)
	return 0

def organize(args,data):
	global d, mismatch
	d = {}
	mismatch = {}

	file_names_changes = 0
	for root,mp3file in search_for_mp3s(args.input,args.verbose):
		# try:
		# 	if args.verbose:
		# 		print "Trying to move file "+mp3file
		# except:
		# 	pass
		if rename_files(root,mp3file,args,data) == 0:
			file_names_changes += 1

	move_folders(args,data,file_names_changes)


def move_folders(args,data,file_names_changes):
	print "\n======================"
	folders_moved = 0
	for key, value in d.iteritems():
		if args.mode == "test":
			if value != False:
				try:
					print key
				except:
					print "???"
				print "->"
				try:
					print value
				except:
					print "???"
				print "======================"
				folders_moved += 1
			else:
				print "Some of the files in "+key+"wanted to go to different folders:"
				for location in mismatch[key]:
					print "'"+location+"'"
				print "The directory was not moved. Please fix the ID3 tags and/or the folder format to make sure it's organized correctly!"
				print "======================"
		else:
			if args.verbose:
				print key, value

			if value != False:
				try:
					shutil.move(key, value)
				except shutil.Error:
					print "ERROR: Folder '"+value+"' already exists. Folder will not be moved from "+key
				folders_moved += 1
			else:
				print "Some of the files in "+key+" wanted to go to different folders:"
				for location in mismatch[key]:
					print "'"+location+"'"
				print "The directory was not moved. Please fix the ID3 tags and/or the folder format to make sure it's organized correctly!"
				print "======================"
	
	if args.mode != "test" and data["Settings"]["remove_empty_directories"]:
		for key in d:
			stop_checking = False
			while not stop_checking:
				for curdir, subdirs, files in os.walk(key):
					if len(subdirs) == 0 and len(files) == 0: #check for empty directories. len(files) == 0 may be overkill
						if args.verbose:
							print 'Removing empty directory: '+curdir #add empty results to file
						os.rmdir(curdir) #delete the directory
					else:
						stop_checking = True
						break
				(key, _) = os.path.split(key)


	if args.verbose:
		if args.mode == 'test':
			print "Empytree finished successfully in test mode! Run with '--mode organize' to actually change something."
			print "  Hypothetical filenames changed:",file_names_changes
			print "  Hypothetical folders moved:", folders_moved
		else:
			print "Empytree finished successfully!"
			print "  Filenames changed:",file_names_changes
			print "  Folders moved:", folders_moved