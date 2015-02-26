import argparse
import os
import os.path
import sys
import glob
import shutil
import re
import eyed3

def remove_banned_words(text):
	if text is None: 
		return u''
	return re.sub(r'(mongolduu\.com|mongolduu)[ -]*', '', text, flags=re.I).strip(' -')

def move_to_correct_path(file_name):
	audiofile = eyed3.load(file_name)
	new_path = '.'
	if audiofile.tag:
		audiofile.tag.artist = remove_banned_words(audiofile.tag.artist)
		audiofile.tag.album = remove_banned_words(audiofile.tag.album)
		audiofile.tag.title = remove_banned_words(audiofile.tag.title)
		audiofile.tag.save()
		if audiofile.tag.artist:
			new_path = os.path.join(new_path, audiofile.tag.artist)
		if audiofile.tag.album:
			new_path = os.path.join(new_path, audiofile.tag.album)
		if not os.path.exists(new_path):
			os.makedirs(new_path)
	new_path = os.path.join(new_path, remove_banned_words(file_name))
	shutil.move(file_name, new_path)

if __name__ == '__main__':
		parser = argparse.ArgumentParser(description='Organize MP3 using ID3 tags.')
	parser.add_argument('--verbose','-v',action='store_true')
	parser.parse_args('--verbose'.split())

	args = parser.parse_args()
	if(args.verbose == True):
		print "Empytree starting..."
	for mp3file in glob.glob('*.mp3'):
		try:
			move_to_correct_path(mp3file)

		except Exception, e:
			sys.stderr.write('Error while fixing "%s": %s' % (mp3file, str(e)))