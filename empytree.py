#!/usr/bin/python
# -*- coding: utf-8 -*-

import os				## Operation system interface
import re 				## Regular expressium operations
import sys  			## System-specific parameters and functions
from glob import glob	## Unix style pathname pattern expansion
import fnmatch			## Matches file names
import shutil			##
import argparse			## Argument parser
import warnings			##
from pdb import set_trace


## External modules
import eyed3	## eyed3 id3 tag module: http://eyed3.nicfit.net/

## Remove all banned words from 
def remove_banned_words(text):
	if text is None: 
		return u''
	return re.sub(r'(mongolduu\.com|mongolduu)[ -]*', '', text, flags=re.I).strip(' -')

## Search for mp3s in spevified input folder
def search_for_mp3s():
	for root, dirnames, filenames in os.walk(args.input):
		for filename in fnmatch.filter(filenames, '*.mp3'):
			yield root, filename


def move_to_correct_path(root,file_name):
	# Get global files
	global FILES_MOVED

	file_name_with_path = os.path.join(root,file_name)
	audiofile = eyed3.load(file_name_with_path)
	new_path = args.output
	if not audiofile.tag:
		warnings.warn("No tag found in file: "+file_name_with_path+". Skipping file.", TagWarning)
		return 0

	audiofile.tag.artist = remove_banned_words(audiofile.tag.artist)
	audiofile.tag.album = remove_banned_words(audiofile.tag.album)
	audiofile.tag.title = remove_banned_words(audiofile.tag.title)
	audiofile.tag.save()

	## 
	if audiofile.tag.artist:
		new_path = os.path.join(new_path, audiofile.tag.artist)
	else:
		warnings.warn("No artist tag found in file: "+file_name, TagWarning)
	if audiofile.tag.album:
		new_path = os.path.join(new_path, audiofile.tag.album)
	if not os.path.exists(new_path):
		os.makedirs(new_path)

	if args.verbose:
		print "New path is "+new_path
	new_path = os.path.join(new_path.encode('utf8'), remove_banned_words(file_name))
	if args.verbose:
		print "New path is "+new_path
	shutil.move(file_name_with_path, new_path)
	if args.verbose:
		print "Moved "+file_name+" to "+new_path
		FILES_MOVED += 1
	return 0

## The Main function
if __name__ == '__main__':
	global FILES_MOVED
	FILES_MOVED = 0

	# Create a argument parser
	parser = argparse.ArgumentParser(description='Organize MP3 using ID3 tags.')
	## Hint: add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
	parser.add_argument('--verbose','-v',action='store_true')
	parser.parse_args('--verbose'.split())

	parser.add_argument('--input','-i',default='',help='The input directory (i.e. where the files you want )',action='store')
	parser.add_argument('--output','-o',default='Music/',help='The input directory (i.e. where the files you want )',action='store')

	# parser.add_argument('--max_depth','-d',default=10,help='The maximum depth Empytree will search for mp3s in your input folder.')

	args = parser.parse_args()

	if not args.input.endswith('/'):
		args.input += '/'
	if not args.output.endswith('/'):
		args.output += '/'
	if args.input.startswith('./'):
		args.input = args.input[2:]
	if args.output.startswith('./'):
		args.output = args.output[2:]

	if args.verbose:
		print "Empytree starting..."
		print "========= Arguments ========="
		print "Verbosity is on!"
		print "Input directory is: "+args.input
		print "Output directory is: "+args.output
		print "============================="

	for root,mp3file in search_for_mp3s():
		if args.verbose:
			print "Trying to move file "+mp3file
		move_to_correct_path(root,mp3file)

	if args.verbose:
		print "Total files moved:",FILES_MOVED