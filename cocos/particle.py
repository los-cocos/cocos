#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
# To see some examples, see:
#    test/test_particle.py
#

import random

from pyglet.gl import *

__all__ = [ 'Particle', 'ParticleEmitter' ]

class Particle(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 25-random.random()*50
        self.vy = random.random()*50
        self.color = (random.random(),random.random(),random.random(),random.random())
        self.lifetime = 3 + random.random() * 3
        self.active = True
        self.angle = 0.0
        self.scale = 1.0
        self.gravity = 20


class ParticleEmitter( object ):

    def __init__( self, n, coords ):
        self.particles = [ Particle() for i in range(n) ]
        self.size = (3,3)
        self.hotspot = (0.5, 0.5)
        self.coords = coords

        self.create_particle()

    def create_particle( self):
        xs,ys = self.size
        hx,hy = self.hotspot
        hx *= -(xs)
        hy *= -(ys)
                
        self.listid = glGenLists(1)
        glNewList(self.listid, GL_COMPILE)

        glBegin(GL_QUADS)
        glVertex2f(hx,hy)
        glVertex2f(hx+xs,hy)
        glVertex2f(hx+xs,hy+ys)
        glVertex2f(hx,hy+ys)
        glEnd()

        glEndList()

    def step( self, dt ):

        x = self.coords[0]
        y = self.coords[1]

        to_be_deleted = []

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
#            glRotatef(p.angle, 0, 0, 1)
#            glScalef( p.scale, p.scale, 1 )
            glTranslatef(p.x + x, p.y+y,0)
            glCallList(self.listid)
            glPopMatrix()

        for p in to_be_deleted:
            self.particles.remove( p )

