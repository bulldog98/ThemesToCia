#!/usr/bin/env python3

import argparse
import os
from collections import namedtuple
import subprocess
from tempfile import TemporaryDirectory
from shutil import copyfile
from distutils.spawn import find_executable

ThemeEntry = namedtuple('ThemeEntry', ['foldername', 'uid'])

tmpDir = TemporaryDirectory()
iconDir = os.path.join(tmpDir.name, 'icons')
os.makedirs(iconDir)

def assertToolsExist():
    assert find_executable('makerom'), 'Install makerom and ensure it is in $PATH'
    assert find_executable('convert'), 'Install imagemagick and ensure it is in $PATH'
    assert find_executable('ffmpeg'), 'Install ffmpeg and make sure is is in $PATH'

def parseCmd():
    parser = argparse.ArgumentParser()
    regionGroup = parser.add_mutually_exclusive_group(required = True)
    regionGroup.add_argument('-e', action='append_const', dest='region', const='e')
    regionGroup.add_argument('-u', action='append_const', dest='region', const='u')
    regionGroup.add_argument('-j', action='append_const', dest='region', const='j')
    regoinGroup.add_argument('-r', '--reverse' action='store_false', help='Sort the themes so they show up in reverse alphabetical order in the 3DS')
    return parser.parse_args()

def convertIcon(theme):
    themeIcon = os.path.join(theme.foldername, 'icon')
    tmpIcon = os.path.join(iconDir, theme.uid)
    if os.path.exists(themeIcon + '.icn'):
        copyfile(themeIcon + '.icn', tmpIcon + '.icn')
    else if [x for x in next(os.walk(theme.foldername))[2] if x.startswith('icon.')]:
        subprocess.call(['convert', themeIcon + '.*', '-resize', '48x48', '-background', 'black', '-gravity' 'center', '-extent', '48x48', tmpIcon + '.png'], shell=True)
        subprocess.call(['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-vcodec', 'png', '-i', tmpIcon + '.png', '-vcodec', 'rawvideo', '-pix_fmt', 'rgb56565', tmpIcon + '.icn'])
        os.remove(tmpIcon + '.png')
    else:
        # TODO parse info.smdh or use default
        raise Error('Not implemented yet')

def strToFixedUtf8(string, length):
    enc = string.encode('utf-8')[:length]
    while True:
        try:
            enc.decode('utf-8')
            break
        except:
            enc = enc[:-1]
    return enc + ((length - len(enc)) * b'\x00')

def isThemeComplete(theme: ThemeEntry):
    files = next(os.walk(theme.foldername))[2]
    return 'body_LZ.bin' in files and 'info.smdh' in files

def listThemes():
    thisDir = os.path.dirname(__file__)
    themeDir = os.path.join(thisDir, 'themes')
    folders = next(os.walk(themeDir))[1]
    i = 0
    for folder in folders:
        yield createThemeEntry(folder, i)
        i += 1

def createThemeEntry(folder, uid):
    raise Error('Not implemented yet')
