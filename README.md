# dancehallstar.py
This is a little helper script to automatically download promos from dancehallstar.net in python.

The urls of the promos get gathered in three iterations by the help of this [tutorial](https://www.geeksforgeeks.org/extract-all-the-urls-from-the-webpage-using-python/). The download from zippyshare is based on [zipPy](https://github.com/ianling/zipPy) by Ianling. In the end all files get unzipped and the archives get deleted.

As dancehallstar.net always shows the latest releases on the first page, you just specify how many pages you wanna go back from the start with the `-d` argument. Plus the directory where to download the files to with `-p`. Simple as that....

# Requirements
* Python 3.6 (or above)
  * requests
  * bs4
  * clint
  * dcryptit>=2.0 (https://github.com/ianling/dcryptit-python)

Install dependencies automatically with pip:

    pip3 install -r requirements.txt

# Usage
    $ python3 dancehallstar.py -h
    usage: dancehallstar.py [-h] -d DEPTH -p PATH

    Download the latest promo from dancehallstar.net

    optional arguments:
      -h, --help            show this help message and exit
      -d DEPTH, --depth DEPTH
                            number of pages to go back
      -p PATH, --path PATH  path to store the files in


# Step by step instruction

## Windows
- install [python3](https://www.python.org/downloads/)
- open the powershell app
- change into the folder of the script: `cd <path to folder>`
- `pip3 install -r requirements.txt`
- `python3 dancehallstar.py -d <depth (any number)> -p <path to save the files>`

## Mac
- install [python3](https://www.python.org/downloads/)
- open the terminal app
- change into the folder of the script: `cd <path to folder>`
- `pip3 install -r requirements.txt`
- `python3 dancehallstar.py -d <depth (any number)> -p <path to save the files>`

In case you experience a "FAILED! Removing temp file" failure, try using a VPN connection.




