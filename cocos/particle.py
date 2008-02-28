#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
# To see some examples, see:
#    test/test_particle.py
#

import random

from pyglet.gl import *
from pyglet import image

__all__ = [ 'Particle', 'ParticleEmitter', 'SmokeParticle', 'SmokeEmitter' ]

class Particle(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 25-random.random()*50
        self.vy = 40+random.random()*30
        self.color = (random.random(),random.random(),random.random(),random.random())
        self.lifetime = 3 + random.random() * 3
        self.active = True
        self.angle = 0.0
        self.scale = 1.0
        self.gravity = 20

class SmokeParticle(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 20-random.random()*40
        self.vy = 20+random.random()*40
        self.color = [1.0, 1.0, 1.0, random.random() ]
        self.lifetime = 4 + random.random() * 3
        self.active = True
        self.angle = 0.0
        self.scale = 1.0
        self.gravity = 20

class ParticleEmitter( object ):

    def __init__( self, n, coords, filename ):
        self.particles = [ Particle() for i in range(n) ]
        self.size = (10,10)
        self.hotspot = (0.5, 0.5)
        self.coords = coords
        self.texture = None

        if filename:
            self.load_texture( filename )

        self.create_particle()


    def load_texture( self, filename ):        
        textureSurface = image.load(filename)
        self.texture=textureSurface.texture

    def create_particle( self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -(xs)
        hy *= -(ys)
                
        self.listid = glGenLists(1)
        glNewList(self.listid, GL_COMPILE)

        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex2f(hx,hy)
        glTexCoord2f(1,0); glVertex2f(hx+xs,hy)
        glTexCoord2f(1,1); glVertex2f(hx+xs,hy+ys)
        glTexCoord2f(0,1); glVertex2f(hx,hy+ys)
        glEnd()

        glEndList()

    def step( self, dt ):

        x = self.coords[0]
        y = self.coords[1]

        to_be_deleted = []

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id )

        for p in self.particles:
            p.lifetime -= dt
            if p.lifetime < 0:
                to_be_deleted.append( p )
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy -= p.gravity * dt

            glPushMatrix()
            glColor4f(*p.color)
            glTranslatef(p.x + x, p.y+y,0)
            glCallList(self.listid)
            glPopMatrix()

        glDisable( GL_TEXTURE_2D )

        for p in to_be_deleted:
            self.particles.remove( p )

    def __del__(self):
        glDeleteLists(self.listid, 1)


class SmokeEmitter( object ):

    def __init__( self, n, coords, filename ):
        self.particles = [ SmokeParticle() for i in range(n) ]
        self.size = (10,10)
        self.hotspot = (0.5, 0.5)
        self.coords = coords
        self.texture = None

        if filename:
            self.load_texture( filename )

        self.create_particle()


    def load_texture( self, filename ):        
        textureSurface = image.load(filename)
        self.texture=textureSurface.texture

    def create_particle( self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -(xs)
        hy *= -(ys)
                
        self.listid = glGenLists(1)
        glNewList(self.listid, GL_COMPILE)

        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex2f(hx,hy)
        glTexCoord2f(1,0); glVertex2f(hx+xs,hy)
        glTexCoord2f(1,1); glVertex2f(hx+xs,hy+ys)
        glTexCoord2f(0,1); glVertex2f(hx,hy+ys)
        glEnd()

        glEndList()

    def step( self, dt ):

        x = self.coords[0]
        y = self.coords[1]

        to_be_deleted = []

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture.id )

        for p in self.particles:
            p.lifetime -= dt
            if p.lifetime < 0:
                to_be_deleted.append( p )
                continue
            p.x += p.vx * dt * 0.15
            p.y += p.vy * dt * 0.15
#            p.vy -= p.gravity * dt

            p.color[3] = p.color[3] - 0.1 * dt;

            glPushMatrix()
            glColor4f(*p.color)
            glTranslatef(p.x + x, p.y+y,0)
            glCallList(self.listid)
            glPopMatrix()

        glDisable( GL_TEXTURE_2D )

        for p in to_be_deleted:
            self.particles.remove( p )

    def __del__(self):
        glDeleteLists(self.listid, 1)
