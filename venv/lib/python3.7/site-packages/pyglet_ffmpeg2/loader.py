#!/usr/bin/python3
# -*- encoding: utf-8 -*-

"""This module provides functions for loading FFmpeg binaries.
"""

import sys
import os
import glob
import pyglet

def load_ffmpeg():
    """Load FFmpeg binaries.
    """

    _locate_binaries()
    if pyglet.media.have_ffmpeg():
        from pyglet.media.codecs import ffmpeg
        pyglet.media.add_decoders(ffmpeg)
    else:
        print("FFmpeg binaries could not be loaded.")


def _locate_binaries():
    """Locate the binaries depending on platform and architecture.

    Once binaries are correctly located, set the relevant environment
    variable to point to the binaries.

    On Windows this is PATH. On Mac OS and linux this is LD_LIBRARY_PATH.
    """

    this_dir = os.path.abspath(os.path.dirname(__file__))

    if sys.platform == 'win32':
        is64bit = sys.maxsize > 2 ** 32

        if is64bit:
            path = os.path.join(this_dir, 'Win64')
        else:
            path = os.path.join(this_dir, 'Win32')

        env_var = 'PATH'

    elif sys.platform == 'darwin':
        path = os.path.join(this_dir, 'MacOS')
        env_var = 'LD_LIBRARY_PATH'

    elif sys.platform.startswith('linux'):
        if 'armv7l' in sys.platform or 'armv7l' in os.uname():
            path = os.path.join(this_dir, 'RPi')
        else:
            path = os.path.join(this_dir, 'linux_x86_64')
            path = path.replace("/lib/", "/lib64/")
        _ensure_linux_symlinks(path)
        env_var = 'LD_LIBRARY_PATH'

    paths = os.environ.get(env_var, '').split(os.pathsep)
    paths.append(path)
    os.environ[env_var] = os.pathsep.join(paths)

    if sys.platform.startswith('linux'):
        # On linux, refresh the cache to take LD_LIBRARY_PATH into account
        pyglet.lib.loader._create_ld_so_cache()


def _ensure_linux_symlinks(bin_folder):
    """Create symlinks to the libav shared binary files.

    On Linux, each so file needs 2 symlinks to work correctly. As it's not possible
    to package symlinks we need to create them manually. This will only run once.
    """
    links = {
        'libavcodec.so.58.*': ('libavcodec.so.58', 'libavcodec.so'),
        'libavformat.so.58.*': ('libavformat.so.58', 'libavformat.so'),
        'libswresample.so.3.*': ('libswresample.so.3', 'libswresample.so'),
        'libavfilter.so.7.*': ('libavfilter.so.7', 'libavfilter.so'),
        'libavutil.so.56.*': ('libavutil.so.56', 'libavutil.so'),
        'libswscale.so.5.*': ('libswscale.so.5', 'libswscale.so')
    }
    for glob_sofile, symlinks in links.items():
        search_path = os.path.join(bin_folder, glob_sofile)
        # print(f"AAA: {search_path}")
        my_glob = glob.glob(search_path)
        # print(f"BBB: {my_glob}")
        if my_glob is not None and len(my_glob) > 0:
            sofile = my_glob[0]
            for symlink in symlinks:
                if not os.path.isfile(os.path.join(bin_folder, symlink)):
                    os.symlink(
                        os.path.join(bin_folder, sofile),
                        os.path.join(bin_folder, symlink)
                    )
        else:
            print(f"Unable to find match for ffmpeg sound library at expected location: {search_path}")
