# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


import cocos
from cocos.director import director

import pyglet
from pyglet import font, image
from pyglet.gl import *
from cocos.actions import ActionSprite
from pyglet.window import key
from cocos.actions import ActionSprite, Rotate, Repeat
from cocos.transitions import *

class HelloWorld(cocos.layer.Layer):
    def __init__(self):

        super( HelloWorld, self ).__init__()

        # see pyglet documentation for help on this lines
        self.text = pyglet.text.Label('Hello, World!', font_name='', font_size=32, x=100, y=240, batch=self.batch)

        
class BackgroundLayer(cocos.layer.Layer):
    """
    """
    def __init__( self, path_name ):
        self.image = image.load(path_name)
        
        
    def step(self, dt):
        texture = self.image.texture
        
        rx = director.window.width - 2*director._offset_x
        ry = director.window.height - 2*director._offset_y
        
        tx = float(rx)/texture.width
        ty = float(ry)/texture.height


        glEnable(GL_TEXTURE_2D)        
        glBindTexture(texture.target, texture.id)

        x, y = director.get_window_size()
        glBegin(gl.GL_QUADS)
        glTexCoord2d(0,0);
        glVertex2f( 0, 0 )
        glTexCoord2d(0,ty);
        glVertex2f( 0, y )
        glTexCoord2d(tx,ty);
        glVertex2f( x, y )
        glTexCoord2d(tx,0);
        glVertex2f( x, 0 )
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        
        
class TitleSubTitleLayer(cocos.layer.Layer):
    def __init__(self, title, subtitle):
        # see pyglet documentation for help on this lines
        ft = font.load('Gill Sans', 64)
        ft2 = font.load('Gill Sans', 52)

        self.title = font.Text(ft, title, x=100, y=150)
        self.subtitle = font.Text(ft2, subtitle, x=100, y=150)
        x, y = director.get_window_size()
        
        self.title.x = x/2 - self.title.width / 2 
        self.title.y = (y/8)*5 - self.title.height / 2 

        self.subtitle.x = x/2 - self.subtitle.width / 2 
        self.subtitle.y = (y/8)*4 - self.subtitle.height / 2 
        
    def step(self, dt):
        # this function is called on every frame
        # dt is the elapsed time between this frame and the last        
        self.title.draw()
        self.subtitle.draw()

class BulletListLayer(cocos.layer.Layer):
    def __init__(self, title, lines):
        x, y = director.get_window_size()


        ft = font.load('Gill Sans', 64)
        self.title = font.Text(ft, title, x=100, y=150)
        self.title.x = x/2 - self.title.width / 2 
        self.title.y = (y/8)*7 - self.title.height / 2 

        start_y = (y/12)*8
        font_size = 52
        done = False
        while not done:
            line_font = font.load('Gill Sans', font_size)
            tot_height = 0
            max_width = 0
            rendered_lines = []
            
            for line in lines:
                line_text = font.Text(line_font, line, y=start_y - tot_height, x=0)
                max_width = max( max_width, line_text.width )
                tot_height += line_text.height*1.2 
                rendered_lines.append( line_text )
                
            if tot_height < start_y:
                done = True
                
            font_size -= 1
            
        start_y = (y/12)*4 + tot_height/2
        
        delta_y = 0
        for line in rendered_lines:
            line.x = x/2 - max_width/2
            line.y = start_y - delta_y
            delta_y += line.height
            
        self.rendered_lines = rendered_lines
        
    def step(self, dt):
        # this function is called on every frame
        # dt is the elapsed time between this frame and the last        
        self.title.draw()
        for line in self.rendered_lines:
            line.draw()
                    
class TransitionControl(cocos.layer.Layer):
    def __init__(self, scenes, transitions=None):
        self.transitions = transitions
        self.scenes = scenes
        for scene in scenes:
            if not self in scene.layers:
                scene.add(0,self,"control")
                
        self.scene_p = 0
        
            
    def next_scene(self):
        self.scene_p +=1 
        if self.scene_p >= len(self.scenes):
            self.scene_p = len(self.scenes)-1
        else:
            self.transition(cocos.transitions.SlideLRTransition)
    
    def prev_scene(self):
        self.scene_p -=1 
        if self.scene_p < 0:
            self.scene_p = 0
        else:
            self.transition()
           
    def transition(self, transition=None):
        if transition:
            director.replace( transition(
                        director.scene,
                        self.scenes[ self.scene_p ],
                        duration = 1
                         )
                )
        else:
            director.replace( self.scenes[ self.scene_p ] )
        
    def on_key_press(self, keyp, mod):
        if keyp in (key.RIGHT, key.ENTER, key.SPACE, key.PAGEDOWN):
            self.next_scene()
        elif keyp in (key.LEFT, key.BACKSPACE, key.PAGEUP):
            self.prev_scene()
            
class RunScene(cocos.layer.Layer):
    def __init__(self, target):
        self.target = target
        
    def on_key_press(self, keyp, mod):
        if keyp in (key.F1,):
            director.push( self.target )    
        
class ControlLayer(cocos.layer.Layer):
    def on_enter( self ):
        ft_title = font.load( "Arial", 32 )
        ft_subtitle = font.load( "Arial", 18 )
        ft_help = font.load( "Arial", 16 )

        self.text_title = font.Text(ft_title, "Transition Demos",
            x=5,
            y=480,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)

        self.text_subtitle = font.Text(ft_subtitle, transition_list[current_transition].__name__,
            x=5,
            y=400,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)
        
        self.text_help = font.Text(ft_help,"Press LEFT / RIGHT for prev/next example, ENTER to restart example",
            x=320,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)

    def step( self, df ):
        self.text_help.draw()

        self.text_subtitle.text = transition_list[current_transition].__name__
        self.text_subtitle.draw()
        self.text_title.draw()

    def on_key_press( self, k , m ):
        global current_transition, control_p
        if k == key.LEFT:
            current_transition = (current_transition-1)%len(transition_list)
        if k == key.RIGHT:
            current_transition = (current_transition+1)%len(transition_list)
        if k == key.ENTER:
            director.replace( transition_list[current_transition](
                        control_list[control_p],
                        (control_list[(control_p+1)%len(control_list)] ),
                        2)                                
                    )
            control_p = (control_p + 1) % len(control_list)
            return True
        if k == key.ESCAPE:
            director.scene.end()
            return True

class GrossiniLayer(cocos.layer.AnimationLayer):
    def __init__( self ):
        super( GrossiniLayer, self ).__init__()

        g = ActionSprite('grossini.png')

        g.place( (320,240,0) )

        self.add( g )

        rot = Rotate( 180, 5 )

        g.do( Repeat( rot ) )

   
class GrossiniLayer2(cocos.layer.AnimationLayer):
    def __init__( self ):
        super( GrossiniLayer2, self ).__init__()

        rot = Rotate( 180, 5 )

        g = ActionSprite('grossini.png')
        g.place( (490,240,0) )
        self.add( g )
        g.do( Repeat( rot ) )

        g = ActionSprite('grossini.png')
        g.place( (150,240,0) )
        self.add( g )
        g.do( Repeat( rot ) )

if __name__ == "__main__":
    director.init()
    
    background = BackgroundLayer("background.png")
    #background = BackgroundLayer("coconut.jpg")
    
    g = GrossiniLayer()
    g2 = GrossiniLayer2()
    c2 = cocos.layer.ColorLayer(0.5,0.1,0.1,1)
    c1 = cocos.layer.ColorLayer(0,1,1,1)
    control = ControlLayer()
    controlScene1 = cocos.scene.Scene(c2, g, control)
    controlScene2 = cocos.scene.Scene(c1, g2, control)
    control_p = 0
    control_list = [controlScene1, controlScene2]
    
    transition_list = [
        SlideLRTransition,
        SlideRLTransition,
        GrowTransition,
        FadeTransition,
        ShrinkAndGrow,
        SlideBTTransition,
        SlideTBTransition,
        MoveInTTransition,
        MoveInBTransition,
        MoveInLTransition,
        MoveInRTransition,
        CornerMoveTransition,
        ]
    current_transition = 0

    scenes = [
        cocos.scene.Scene (background, 
        TitleSubTitleLayer("cocos", "a game library"),
        ),
        cocos.scene.Scene (background, 
            BulletListLayer("Features", [
                "Scene manager",
                "Transitions between scenes",
                "Action Sprites",
                "Special effects in layers",
                "pyglet / opengl based",
                "Documented: Programming Guide \n+ API Reference",
                ]),
        ),
        cocos.scene.Scene (background, 
            BulletListLayer("Scene Manager", [
                "problem with state machines",
                "how we solve it",
                "return values",
                ]),
        ),
        cocos.scene.Scene (background, 
            BulletListLayer("Transitions", [
                "render to texture",
                "read from colorbuffer",
                "both scenes are live",
                "no events propagate"
                ]),
            RunScene( controlScene1 )
                
        ),
        cocos.scene.Scene (background, 
            BulletListLayer("Closing", [
                "http://code.google.com/p/los-cocos/"," ",
                "pyweek approved",
                "see you there!"," "," "," "," ",
                ]),
        ),
    ]
    transitions = [None]*(len(scenes)-1)
    transitions[0]=cocos.transitions.SlideRLTransition
    TransitionControl( scenes, transitions )
    
    
    director.run (scenes[0])

