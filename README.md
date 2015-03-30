# empytree
Empytree is a cross-platform MP3 music organizer. The goal of the project is to create a command line tool to keep music databases well organized. The tool is built so it can easily be used in a pipeline with BitTorrent clients.

**Note:** The project is currently ready to use but has very limited features. Make sure you verify everything is correct using the `--mode test` argument before using the tool. However, if something unexpected happens note that Empytree is does not remove anything except empty directories so no data should ever be lost because of it. If you'd like a more advanced tool like empytree, I recommend [beets](https://github.com/sampsyo/beets).

## Prerequisites
Uses a python module called [eyeD3](http://eyed3.nicfit.net/). You can install it on Ubuntu with the following:

    $ sudo pip install --allow-unverified eyed3 eyed3

## Installation
### Basic setup
* Step 1: Clone or download this repository.
* Step 2: Change the configuration file, config.json, to your liking (more info below).
* Step 3 (optional): Run empytree in test mode

    `$ python empytree.py --mode test`

   It will display which files empytree would hypothetically rename and also where it would move your directories with mp3 files. Repeat step 2 if you're unhappy with the results.
* Step 4: Run empytree!

    `$ python empytree.py --mode organize`

### Help
For more options run

	$ python empytree.py --help

### Configuration
By default Empytree will read the configuration file named 'config.json' in the same directory. If you want to use a different configuration file you can pass in a '--config /path/to/config/config_name.json' argument. This escpecially useful if you want to use multiple configuration files. In the configuration files there should be 3 JSON objects:

#### The 'Folders' JSON object
The Folders object has the following properties:
* input: The location of the directories to scan. Can accept multiple directories.
* output: The root location that Empytree will move your mp3s. Can only accept a single directory.

Remember to use full paths if you want to be able to run Empytree at any location.

#### The 'ArtistFormat' JSON object
Here you choose the format of your directories. 'ArtistFormat' will be used when the album artist and artist are the same (or there is no album artist). The first item in the array is your top level directory format, the next will be its subdirectory, and so on. There's no limition how many levels of directories can be used. The default settings will use 4 levels on the format:

	Music/%(artist_append_the)s/[%(year)s] %(album)s/%(disc_num)s%(track_num_2)s-%(artist)s-%(title)s.mp3
	Music/Smashing Pumpkins, The/[2001] Greatest Hits/107-smashing_pumpkins-bullet_with_butterfly_wings.mp3

The available properties are:
* **format** is the format of your directory/file. Wildcards are allowed (see below).
* **lowercase** will force the folder/file to be all in lowercase.
* **uppercase** will force the folder/file to be all in uppercase.
* **replaceSpaces** will replace spaces with underscores.

#### The 'VAFormat' JSON object
Same as 'ArtistFormat' but is used then artist and album artists aren't the same. The default format is:

VA/%(album)s/%(disc_num)s%(track_num_2)s-%(artist)s-%(title)s.mp3
VA/Top 50 Songs of 1996/01-robert_miles-children.mp3

#### Settings
The only changable setting is currently: remove_empty_directories. By default it's set to True. If True the script will check if the supdirectories of the directory moved are empty and if so, delete them. 

### Available wildcards are:
* `%(album)s`
* `%(album_artist)s`
* `%(artist)s`
* `%(artist_append_the)s`: Remove 'The', but then appends it as ', The' behind the artist name.
* `%(artist_first_letter)s`: Only the first letter of the artist.
* `%(artist_no_the)s`: Skips 'The' from artist name
* `%(artist_or_va)s`: uses VA as artist if artist and album artist aren't the same (or album artist is empty).
* `%(disc_num)s`
* `%(disc_num_2)s`: Disk number with leading zeros to force 2 digit long string.
* `%(title)s`
* `%(track_num)s`
* `%(track_num_2)s`: Track number with leading zeros.
* `%(year)s`