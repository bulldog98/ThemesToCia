#!/usr/bin/env python3
"""This handles packaging of 3ds themes into a cia"""

import argparse
import os
import subprocess
import tempfile
from collections import namedtuple
from distutils.spawn import find_executable
from shutil import copyfile


ThemeEntry = namedtuple('ThemeEntry', ['foldername', 'uid'])

TMPDIR = TemporaryDirectory()
NORMALIZEDTHEMES = os.path.join(TMPDIR.name, 'themes')
os.makedirs(NORMALIZEDTHEMES)


def assert_tools_exist():
    """Asserts that all required tools are in the path"""
    assert find_executable('makerom'), \
        'Install makerom and ensure it is in $PATH'
    assert find_executable('convert'), \
        'Install imagemagick and ensure it is in $PATH'
    assert find_executable('ffmpeg'), \
        'Install ffmpeg and make sure is is in $PATH'


def parse_cmd():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    region_group = parser.add_mutually_exclusive_group(required=True)
    region_group.add_argument(
        '-e', action='append_const', dest='region', const='e')
    region_group.add_argument(
        '-u', action='append_const', dest='region', const='u')
    region_group.add_argument(
        '-j', action='append_const', dest='region', const='j')
    parser.add_argument(
        '-r', '--reverse', action='store_false',
        help='Sort the themes so they show up in reverse ' +
        'alphabetical order in the 3DS')
    return parser.parse_args()


def get_icon(source, dest):
    """get the icon out of source into dest"""
    theme_icon = os.path.join(source, 'icon')
    tmp_icon = os.path.join(dest, 'icon')
    info_smdh = os.path.join(source, 'info.smdh')
    if os.path.exists(theme_icon + '.icn'):
        copyfile(theme_icon + '.icn', tmp_icon + '.icn')
    elif [x for x in (next(os.walk(source))[2]) if x.startswith('icon.')]:
        subprocess.call(
            ['convert', theme_icon + '.*', '-resize', '48x48',
             '-background', 'black', '-gravity' 'center', '-extent', '48x48',
             tmp_icon + '.png'],
            shell=True)
        subprocess.call(
            ['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-vcodec', 'png',
             '-i', tmp_icon + '.png', '-vcodec', 'rawvideo', '-pix_fmt',
             'rgb56565', tmp_icon + '.icn'])
        os.remove(tmp_icon + '.png')
    elif os.path.exists(info_smdh):
        with open(info_smdh, 'rb') as file_handle:
            file_handle.seek(0x24C0)
            icon = file_handle.read(0x1200)
            with open(tmp_icon + '.icn', 'w') as icon_file:
                icon_file.write(icon)
    else:
        # TODO(default) use default
        raise Exception('Not implemented yet')


def str_to_fixed_utf8(string, length):
    """convert stirng to utf-8 and get it to exact length"""
    enc = string.encode('utf-8')[:length]
    while True:
        try:
            enc.decode('utf-8')
            break
        except Exception:
            enc = enc[:-1]
    return enc + ((length - len(enc)) * b'\x00')


def is_theme_complete(folder):
    """checks weather all the nessesary files for a theme are within folder"""
    files = next(os.walk(folder))[2]
    return 'body_LZ.bin' in files and 'info.smdh' in files


def process_themes():
    """This function preprocesses all themes and returns a list of them"""
    this_dir = os.path.dirname(__file__)
    theme_dir = os.path.join(this_dir, 'Themes')
    folders = next(os.walk(theme_dir))[1]
    i = 0
    for folder in folders:
        if not is_theme_complete(os.path.join(theme_dir, folder)):
            continue
        yield process_theme(folder, i)
        i += 1


def try_copy(source, dest):
    """if source exists it copies source to dest"""
    if os.path.exists(source):
        copyfile(source, dest)


def process_theme(folder, uid):
    """This function preprocesses the theme and returns a ThemeEntry for it"""
    theme_dir = os.path.join(NORMALIZEDTHEMES, uid)
    os.makedirs(theme_dir)
    try_copy(os.path.join(folder, 'body_LZ.bin'), theme_dir)
    # TODO(fileneeded) figure out if we need this file
    try_copy(os.path.join(folder, 'info.smdh'), theme_dir)
    try_copy(os.path.join(folder, 'bgm.bcstm'), theme_dir)
    get_icon(folder, theme_dir)
    return ThemeEntry(folder, uid)


def do_conversion(region, reverse):
    """This function does the conversion of the themes for the region"""
    themes = process_themes()
    # Remember that the 3DS wants the theme list reversed, so it is in
    # alphabetical order
    raise Exception('not implemented yet')


if __name__ == '__main__':
    arguments = parse_cmd()
    do_conversion(arguments.region[0], arguments.reverse)
