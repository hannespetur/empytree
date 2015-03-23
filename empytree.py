#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse					## Argument parser
import json						## json is used for reading the config
# from pdb import set_trace

## Local files
from organizer import *

## The Main function
if __name__ == '__main__':
	# Create a argument parser
	parser = argparse.ArgumentParser(description='Empytree organizes MP3s using ID3 tags.')

	## Hint: add_argument(name or flags...[, action][, nargs][, const][, default][, type][, choices][, required][, help][, metavar][, dest])
	parser.add_argument('--verbose','-v',action='store_true')
	parser.add_argument('--mode','-m',default='test',action='store', choices=['test','organize','deluge'])
	parser.add_argument('--config','-c',default='config.json',help='Location of the config.json file',action='store')

	args = parser.parse_args()
	
	json_data = open(args.config,'r')
	global data
	data = json.load(json_data)
	json_data.close()
	args.input = data["Folders"]["input"]
	args.output = data["Folders"]["output"]
	args.output = unicode(args.output)

	# Print out which arguments are defined as what
	if args.verbose:
		print "Empytree is starting..."
		print "========= Arguments ========="
		print "Verbosity is on!"
		print "Running on test mode?",args.mode == "test"
		print "Output directory is: "+args.output
		print "============================="

	organize(args,data)