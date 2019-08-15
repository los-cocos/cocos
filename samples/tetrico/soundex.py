#
# original file from http://www.partiallydisassembled.net/make_me/
# modified later for this game
#
from __future__ import division, print_function, unicode_literals

from constants import MUSIC, SOUND
import pyglet

try:
    import pyglet.media.avbin
    have_avbin = True
except:
    pyglet.options['audio'] = ('silent')
    have_avbin = False
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

    if not have_avbin:
        return

    if name == current_music:
        return
    current_music = name

    if not MUSIC:
        return

    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    # pyglet bug
    music_player.volume = music_player.volume
    music_player.eos_action = 'loop'

def music_volume(vol):
    music_player.volume=vol

def queue_music(name):
    global current_music

    if not have_avbin:
        return

#    if name == current_music:
#        return

    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.eos_action = 'next'


def play_music():
    if music_player.playing or not current_music:
        return

    if not have_avbin:
        return

    name = current_music
    music_player.next()
    music_player.queue(pyglet.resource.media(name, streaming=True))
    music_player.play()
    music_player.eos_action = 'loop'

@music_player.event
def on_eos():
    music_player.eos_action = 'loop'


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
