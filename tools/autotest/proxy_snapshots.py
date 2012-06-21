import sys
import os

import remembercases.snapshot_taker as st

import random
# seed random for repeteability
random.seed('123')

import pyglet
import cocos
from cocos.director import director
import cocos.custom_clocks as cc

pyglet.resource.path.append(os.path.abspath('.'))
pyglet.resource.reindex()

def set_init_interceptor():
    _director_init = director.init
    def director_init_interception(*args, **kwargs):
        _director_init(*args, **kwargs)
        #sys.stderr.write('\nin director_init_interception')

    director.init = director_init_interception

def quit_pyglet_app():
    #sys.stderr.write('\nin quit_pyglet_app')
    pyglet.app.exit()

def take_snapshot_cocos_app(fname):
    pyglet.image.get_buffer_manager().get_color_buffer().save(fname)
    #sys.stderr.write('\nafter take_snapshot_cocos_app')
    

# script_name the basename only
def main(script_name, stored_testinfo, snapshots_dir):
    # do interceptions and other setup task here
    # ...
    sys.path.insert(0, os.getcwd())
    module_name = script_name[:script_name.rfind('.py')]
    print 'module name:', module_name
    s = "import %s as script_module"%module_name
    exec(s)

    if stored_testinfo != script_module.testinfo:
        sys.stderr.write("Es01 - received testinfo doesn't match script testinfo. (db outdated?)\n")
        sys.exit(1)

    screen_sampler, diagnostic = st.ScreenSampler.sampler(stored_testinfo,
                                    script_name,
                                    fn_quit=quit_pyglet_app,
                                    fn_take_snapshot=take_snapshot_cocos_app,
                                    snapshots_dir=snapshots_dir)
    assert diagnostic == ''
    clock = cc.get_autotest_clock(screen_sampler)
    cocos.custom_clocks.set_app_clock(clock)
    
    set_init_interceptor()
    #sys.stderr.write('\nafter interceptor')
    if hasattr(script_module, 'autotest'):
        # allows the script to know if running through autotest
        script_module.autotest = 1
    script_module.main()

if __name__ == '__main__':
    main(*sys.argv[1:])
