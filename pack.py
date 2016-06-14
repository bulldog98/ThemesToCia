#!/usr/bin/env python3

import argparse
import os
import subprocess
from collections import namedtuple
from distutils.spawn import find_executable
from shutil import copyfile
from tempfile import TemporaryDirectory

ThemeEntry = namedtuple('ThemeEntry', ['foldername', 'uid'])

tmpDir = TemporaryDirectory()
normalizedThemes = os.path.join(tmpDir.name, 'themes')
os.makedirs(normalizedThemes)


def assertToolsExist():
    assert find_executable('makerom'), \
        'Install makerom and ensure it is in $PATH'
    assert find_executable('convert'), \
        'Install imagemagick and ensure it is in $PATH'
    assert find_executable('ffmpeg'), \
        'Install ffmpeg and make sure is is in $PATH'


def parseCmd():
    parser = argparse.ArgumentParser()
    regionGroup = parser.add_mutually_exclusive_group(required=True)
    regionGroup.add_argument('-e', action='append_const', dest='region',
                             const='e')
    regionGroup.add_argument('-u', action='append_const', dest='region',
                             const='u')
    regionGroup.add_argument('-j', action='append_const', dest='region',
                             const='j')
    parser.add_argument('-r', '--reverse', action='store_false',
                        help='Sort the themes so they show up in reverse ' +
                        'alphabetical order in the 3DS')
    return parser.parse_args()


def getIcon(source, dest):
    themeIcon = os.path.join(source, 'icon')
    tmpIcon = os.path.join(dest, 'icon')
    infoSmdh = os.path.join(source, 'info.smdh')
    if os.path.exists(themeIcon + '.icn'):
        copyfile(themeIcon + '.icn', tmpIcon + '.icn')
    elif [x for x in (next(os.walk(source))[2]) if x.startswith('icon.')]:
        subprocess.call(
            ['convert', themeIcon + '.*', '-resize', '48x48',
             '-background', 'black', '-gravity' 'center', '-extent', '48x48',
             tmpIcon + '.png'],
            shell=True)
        subprocess.call(
            ['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-vcodec', 'png',
             '-i', tmpIcon + '.png', '-vcodec', 'rawvideo', '-pix_fmt',
             'rgb56565', tmpIcon + '.icn'])
        os.remove(tmpIcon + '.png')
    elif os.path.exists(infoSmdh):
        with open(infoSmdh, 'rb') as f:
            f.seek(0x24C0)
            icon = f.read(0x1200)
            with open(tmpIcon + '.icn', 'w') as iconFile:
                iconFile.write(icon)
    else:
        # TODO(default) use default
        raise Exception('Not implemented yet')


def strToFixedUtf8(string, length):
    enc = string.encode('utf-8')[:length]
    while True:
        try:
            enc.decode('utf-8')
            break
        except Exception:
            enc = enc[:-1]
    return enc + ((length - len(enc)) * b'\x00')


def isThemeComplete(folder):
    files = next(os.walk(folder))[2]
    return 'body_LZ.bin' in files and 'info.smdh' in files


def processThemes():
    thisDir = os.path.dirname(__file__)
    themeDir = os.path.join(thisDir, 'themes')
    folders = next(os.walk(themeDir))[1]
    i = 0
    for folder in folders:
        if not isThemeComplete():
            continue
        yield processTheme(folder, i)
        i += 1


def tryCopy(source, dest):
    if os.path.exists(source):
        copyfile(source, dest)


def processTheme(folder, uid):
    themeDir = os.path.join(normalizedThemes, uid)
    os.makedirs(themeDir)
    tryCopy(os.path.join(folder, 'body_LZ.bin'), themeDir)
    # TODO(fileneeded) figure out if we need this file
    tryCopy(os.path.join(folder, 'info.smdh'), themeDir)
    tryCopy(os.path.join(folder, 'bgm.bcstm'), themeDir)
    getIcon(folder, themeDir)

    return ThemeEntry(folder, uid)


def doConversion(region, reverse):
    raise Exception('not implemented yet')


if __name__ == '__main__':
    args = parseCmd()
    doConversion(args.region[0], args.reverse)
