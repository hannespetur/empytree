## External modules
import eyed3	## eyed3 id3 tag module: http://eyed3.nicfit.net/
eyed3.log.setLevel("ERROR") 	## Avoid getting tons of warnings, turn off if you want to debug.

import string

## Usage:  valid_text = make_file_name_valid(text)
## Before: text is a string.
## After:  valid_text is the same string as text but doesn't have any characters that
##         could potentially be invalid on any operating system.
def make_file_name_valid(file_name):
	valid_chars = "-_,()[] %s%s" % (string.ascii_letters, string.digits)
	return ''.join(c for c in file_name if c in valid_chars)

## Usage:  tag = getTag(file_name_with_path)
## Before: Full path to a file to get ID3 tag from.
## After:  If the file can be successfully read, return the tag for the file,
##         otherwise return False.
def getTag(file_name_with_path):
	# Let's try to read the file
	try:
		audiofile = eyed3.load(file_name_with_path)
		if not audiofile:
			raise Exception("No audiofile read.")
	except:
		try:
			print "Warning: Error reading file with filename: '"+file_name_with_path+"'. Skipping file."
		except:
			print "Warning: Error reading file with filename: ??? Skipping file."
		return False

	# Check if the tags are valid
	if not validate_id3_tags(audiofile.tag,file_name_with_path):
		return False

	# All is good, return the tag
	return audiofile.tag

## Usage:  b = validate_id3_tags(tag,file_name)
## Before: Tag is a valid ID3 tag or False
## After:  Return True if the tag is valid, else return False.
def validate_id3_tags(tag,file_name):
	if not tag:
		return False
	
	if (tag.artist is None) or (len(tag.artist) == 0):
		try:
			print "Warning: Could not find artist tag in file '"+file_name+"' Skipping file."
		except:
			print "Warning: Could not find artist tag in file ??? Skipping file."
		return False
	
	if (tag.album is None) or (len(tag.album) == 0):
		try:
			print "Warning: Could not find album tag in file '"+file_name+"' Skipping file."
		except:
			print "Warning: Could not find album tag in file ??? Skipping file."
		return False
	
	if (tag.title is None) or (len(tag.title) == 0):
		try:
			print "Warning: Could not find title tag in file '"+file_name+"' Skipping file."
		except:
			print "Warning: Could not find title tag in file ??? Skipping file."
		return False
	
	if (tag.track_num is None) or (len(tag.track_num) == 0):
		try:
			print "Warning: Could not find track number tag in file '"+file_name+"' Skipping file."
		except:
			print "Warning: Could not find track number tag in file ??? Skipping file."
		return False
	return True

## Usage:  text_titlecased = titlecase(text)
## Before: text is some string.
## After:  The same text but titlecased, i.e. every word (except 'the', 'and', etc.)
##         with the first character uppcased.
def titlecase(text):
	banned = ['the','and','a']
	lst = []
	for i,word in enumerate(text.split()):
		if(word not in banned or i == 0):
			lst.append(word[0].upper()+word[1:])
		else:
			lst.append(word)
	return lst