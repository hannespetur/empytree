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
import json						## json
from StringIO import StringIO
from pdb import set_trace
from pprint import pprint		## Just for testing purposes


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
	file_name_with_path = os.path.join(root,file_name)
	audiofile = eyed3.load(file_name_with_path)
	new_path = args.output
	if not audiofile.tag:
		warnings.warn("No tag found in file: "+file_name_with_path+". Skipping file.", TagWarning)
		return -1

	audiofile.tag.artist = remove_banned_words(audiofile.tag.artist)
	audiofile.tag.album = remove_banned_words(audiofile.tag.album)
	audiofile.tag.title = remove_banned_words(audiofile.tag.title)
	audiofile.tag.save()

	##
	for level,L in enumerate(data["TreeFormat"]):
		Lformat = L["format"]
		Luc = L["uppercase"]
		Llc = L["lowercase"]
		Lrs = L["replaceSpaces"]
		if level == (len(data["TreeFormat"])-1):
			if not Lformat.endswith('.mp3'):
				Lformat += '.mp3'
		print Lformat, Luc, Llc, Lrs
		# TODO: Replace wildcards and then organize...

	if audiofile.tag.artist:
		new_path = os.path.join(new_path, audiofile.tag.artist)
	else:
		warnings.warn("No artist tag found in file: "+file_name, Warning)

	if audiofile.tag.album:
		new_path = os.path.join(new_path, audiofile.tag.album)

	if not os.path.exists(new_path):
		os.makedirs(new_path)

	new_path = os.path.join(new_path.encode('utf8'), remove_banned_words(file_name))
	if (file_name_with_path==new_path):
		return -1

	if args.test:
		print file_name_with_path+" -> "+new_path
	else:
		shutil.move((file_name_with_path==new_path), new_path)
		if args.verbose:
			print "Moved "+file_name+" to "+new_path

	return 0

## The Main function
if __name__ == '__main__':
	# Create a argument parser
	parser = argparse.ArgumentParser(description='Empytree organizes MP3s using ID3 tags.')

	## Hint: add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
	parser.add_argument('--verbose','-v',action='store_true')
	parser.add_argument('--test','-t',action='store_true')
	parser.add_argument('--input','-i',default='',help='The input directory (i.e. where the files you want to organize).',action='store')
	parser.add_argument('--output','-o',default='Music/',help='The output directory (i.e. where you want to move your files).',action='store')
	parser.add_argument('--config','-c',default='config.json',help='Location of the config.json file',action='store')

	args = parser.parse_args()

	# Format the args to a standard format
	if not args.input.endswith('/'):
		args.input += '/'
	if not args.output.endswith('/'):
		args.output += '/'
	if args.input.startswith('./'):
		args.input = args.input[2:]
	if args.output.startswith('./'):
		args.output = args.output[2:]

	try:
		json_data = open('config.json','r')
		global data, levels
		data = json.load(json_data)
		levels = len(data["TreeFormat"])
		pprint(data)
		json_data.close()
	except:
		warnings.warn("Could not use config: '"+args.config+"'. Either the config was not found or not valid. Using default options.", Warning)

	# Print out which arguments are defined as what
	if args.verbose:
		print "Empytree starting..."
		print "========= Arguments ========="
		print "Verbosity is on!"
		print "Running on test mode?",args.test
		print "Input directory is: "+args.input
		print "Output directory is: "+args.output
		print "============================="

	files_moved = 0
	for root,mp3file in search_for_mp3s():
		# if args.verbose:
		# 	print "Trying to move file "+mp3file
		if not move_to_correct_path(root,mp3file):
			files_moved += 1

	if args.verbose:
		print "Empytree finished successfully! Total files moved:",files_moved