#
# original file from http://www.partiallydisassembled.net/make_me/
# modified later for this game
#
from __future__ import division, print_function, unicode_literals
import os

from constants import MUSIC, SOUND
import pyglet

try:
    import pyglet_ffmpeg2
except ImportError:
    pyglet_ffmpeg2 = None

if pyglet_ffmpeg2:
    try:
        pyglet_ffmpeg2.load_ffmpeg()
    except Exception as ex:
        print("While trying to use ffmpeg audio from package pyglet_ffmpeg2 an exception was rised:")
        print(ex)

try:
    decoders = pyglet.media.codecs._decoder_extensions.get(".mp3", [])
except Exception:
    decoders = None

if decoders:
    have_mp3 = True
else:
    print("warn: cocos running with no sound, no mp3 decoder found.")
    print("      Try installing pyglet_ffmpeg2.")
    pyglet.options['audio'] = ('silent',)
    have_mp3 = False
    MUSIC = False
    SOUND = False

#
# MUSIC
#
music_player = pyglet.media.Player()
current_music = None

sound_vol = 0.7
music_player.volume = 0.4

def set_music(name): 
    global current_music
    current_music = name

def music_volume(vol):
    "sets player volume, vol a float between 0 and 1"
    music_player.volume=vol

def play_music(): 
    if music_player.playing or not current_music:
        return
    if not have_mp3:
        return
                           
    name = current_music
    music_player.next_source()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.volume = music_player.volume
    music_player.loop = True

def stop_music():
#    import pdb
#    pdb.set_trace()
    music_player.pause()

#
# SOUND
#
sounds = {}

def load(name, streaming=False):
    if not SOUND:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=streaming)

    return sounds[name]

def play(name):
    if not SOUND:
        return
    load(name)
    a = sounds[name].play().volume = sound_vol

def sound_volume( vol ):
    global sound_vol
    sound_vol = vol
