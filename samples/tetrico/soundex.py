from constants import MUSIC, SOUND
import pyglet

music_player = pyglet.media.Player()
current_music = None

try:
    import pyglet.media.avbin
    have_avbin = True
except:
    have_avbin = False
    MUSIC = False

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
    music_player.eos_action = 'loop'


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

sounds = {}

def load(name, streaming=False):
    if not SOUND:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=streaming)

    return sounds[name]

def play(name):
    load(name)
    sounds[name].play()

move_player = pyglet.media.Player()

def start_move(name):
    global current_move

    if not SOUND:
        return

    if name not in sounds:
        sounds[name] = pyglet.resource.media(name, streaming=False)

    move_player.next()
    move_player.queue(sounds[name])
    move_player.play()
    move_player.eos_action = 'loop'

def stop_move():
    move_player.pause()
