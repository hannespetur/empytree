# empytree
Empytree is a cross-platform MP3 music organizer. The goal of the project is to create a command line tool to keep music databases well organized. The tool is built so it can easily be used 

**Note:** It's currently in development and non-functional at the moment.

## Prerequisites
Uses a python module called [eyeD3](http://eyed3.nicfit.net/). You can install it on Ubuntu with the following:

    $ sudo pip install --allow-unverified eyed3 eyed3

## Installation
### Basic setup
* Step 1: Clone or download this repository to a directory of your choice.
* Step 2: Change the configuration file, config.json, to your liking (more info below).
* Step 3 (optional): Run empytree in test mode

    `$ python empytree.py --test`

   It will display which files empytree would hypothetically move and where it would move them. Repeat step 2 if you're unhappy with the results.
* Step 4: Run empytree!

    `$ python empytree.py`

### Configuration
By default Empytree will read the configuration file named 'config.json' in the same directory. If you want to use a different configuration file you can pass in a '--config /path/to/config/config_name.json' argument. This escpecially useful if you want to use multiple configuration files.

#### The 'Folders' JSON object
The Folders object has the following properties:
* input: The location of the directories to scan. Can accept multiple directories seperated by a comma (,).
* output: The root location that Empytree will move your mp3s. Can only accept a single directory.

Specifying folders in commandline will override these options. Remember to use full paths if you want to be able to run Empytree at any location.

#### The 'TreeFormat' JSON object
Here you choose the format of your directories. The first item in the array is your top level directory format, the next will be its subdirectory, and so on. There's no limition how many levels of directories can be used. The default settings will use 3 levels on the format:

	$ARTIST/[$YEAR] $ALBUM/$DISK_NUM$TRACK_NUM-$ARTIST-$TRACK_TITLE.mp3
	Savant/[2012] Vario/03-savant-living_ipod.mp3

The available properties are:
* **format** is the format of your directory/file. Wildcards are allowed (see below).
* **lowercase** will force the folder/file to be all in lowercase.
* **uppercase** will force the folder/file to be all in uppercase.
* **replaceSpaces** will replace spaces with underscores.

Available wildcards are:
* `$ARTIST`
* `$ARTIST_OR_VA` (uses VA as artist if artist and album artist isn't the same name.)
* `$ALBUM`
* `$ALBUM_ARTIST`
* `$DISK_NUM`
* `$GENRE`
* `$YEAR`