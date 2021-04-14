import requests
from bs4 import BeautifulSoup
from clint.textui import progress
from dcryptit import read_dlc
from optparse import OptionParser
from os import remove
from os.path import isfile, getsize
from re import match
from requests import get
from sys import exit
from urllib.parse import unquote
import argparse
from zipfile import ZipFile
import os
from os import listdir
from os.path import isfile, join

'''
usage: dancehallstar.py [-h] -d DEPTH -p PATH

Download the latest promo from dancehallstar.net

optional arguments:
  -h, --help            show this help message and exit
  -d DEPTH, --depth DEPTH
                        number of pages to go back
  -p PATH, --path PATH  path to store the files in
'''


def unzip(filelist):
    for file in filelist:
        with ZipFile(file, 'r') as zipObj:
            # Extract all the contents of zip file in current directory
            zipObj.extractall(path)
            zipObj.close()
        os.remove(file)


def filterSet(data:set, fltr_in, fltr_out):
    if fltr_out == None:
        return {x for x in data if fltr_in in x}
    else:
        return {x for x in data if fltr_in in x and fltr_out not in x}

def crawlURL(url):
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')
    urls = set()
    for link in soup.find_all('a'):
        tmp = link.get('href')
        urls.add(tmp)
    return urls

def downloadZippy(url_list, output_dir):
    #code adopted from https://github.com/ianling/zipPy
    filelist=set()
    total_urls = len(url_list)
    successes = 0
    failures = 0
    skips = 0
    max_attempts = 3
    current_url_number = 0
    for url in url_list:
        attempts = 0
        current_url_number += 1
        finished_download = False
        skipped = False
        while attempts <= max_attempts and not finished_download and not skipped:
            attempts += 1
            try:
                subdomain, file_id = match('http[s]?://(\w+)\.zippyshare\.com/v/(\w+)/file.html', url).groups()
            except:
                print(f'Failed to parse URL, skipping: {repr(url)}')
                skipped = True
                continue
            try:
                landing_page = get(url)
            except:
                print('Could not GET URL: {url}')
                continue
            cookies = landing_page.cookies
            landing_page_content = landing_page.text.split('\n')
            for line in landing_page_content:
                if finished_download:
                    break
                if "document.getElementById('dlbutton').href" in line:
                    try:
                        page_parser = match('\s*document\.getElementById\(\'dlbutton\'\)\.href = "/([p]?d)/\w+/" \+ \((.*?)\) \+ "/(.*)";', line).groups()
                    except:
                        print(f"***** ERROR DOWNLOADING: {url})")
                        print(f"FAILED TO PARSE DOWNLOAD URL FROM: {line}")
                        break
                    # TODO: download URLs sometimes have /pd/ instead of /d/, I am not sure why yet. This causes downloads to fail
                    url_subfolder = page_parser[0].replace('pd', 'd')
                    modulo_string = eval(page_parser[1])
                    file_url = page_parser[2]
                    filename = unquote(file_url)
                    path = output_dir + filename
                    if isfile(path):
                        if getsize(path) == 0:
                            print('File already exists, but size is 0 bytes. Deleting empty file and continuing download...')
                            remove(path)
                        else:
                            print(f'File already exists, skipping: {filename}')
                            skipped = True
                            break
                    download_url = f'https://{subdomain}.zippyshare.com/{url_subfolder}/{file_id}/{modulo_string}/{file_url}'
                    while not finished_download:
                        print(f'Downloading ({current_url_number}/{total_urls}): {filename} (attempt {attempts}/{max_attempts})')
                        try:
                            file_download = get(download_url, stream=True, cookies=cookies)
                            with open(path, 'wb') as f:
                                total_length = int(file_download.headers.get('content-length'))
                                for chunk in progress.bar(file_download.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                                    if chunk:
                                        f.write(chunk)
                                        f.flush()
                            finished_download = True
                            if finished_download:
                                filelist.add(path)
                            successes += 1
                        except:
                            attempts += 1
                            break
        if not finished_download and not skipped:
            failures += 1
            print('FAILED! Removing temp file')
            print('Failed landing page URL: {url}')
            print('Failed download URL: {download_url}')
            try:
                remove(path)
            except:
                pass
            print('Moving to next URL...')
        if skipped:
            skips += 1
    print(f'\nSummary: {successes} successful, {failures} failed, {skips} skipped')
    return filelist

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download the latest promo from dancehallstar.net')
    parser.add_argument('-d', '--depth',required=True,type=int, help='number of pages to go back')
    parser.add_argument('-p', '--path',required=True,type=str, help='path to store the files in')

    args = parser.parse_args()
    path=args.path
    if not path.endswith('/'):
        path += '/'
    if not os.path.exists(path):
        os.mkdir(path)
    depth=args.depth
    page = 'https://www.dancehallstar.net/page/'
    for i in range(depth):
        print('\nGathering promos for %s\n' % (page+str(i+1)))
        promos=filterSet(crawlURL(page+str(i+1)),'-promo-', '#respond')
        print('Found %d promos on %s\n' % (len(promos),page+str(i+1)))
        tmpurls=set()
        for url in promos:
            tmpurls.add(filterSet(crawlURL(url), '?id=', None).pop())
        zippy = set()
        for url in tmpurls:
            zippy.add(filterSet(crawlURL(url), 'zippy', None).pop())
        zippy=list(zippy)
        zippy=[x.strip(' ') for x in zippy]
        print('Downloading %d promos from %s' % (len(promos),page+str(i+1)))
        print(64*'*')
        filelist=downloadZippy(zippy,path)
        print('\nExtracting archives to %s\n' % path)
        print(64*'*')
        unzip(filelist)