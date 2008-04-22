#
# Cocos:
# http://code.google.com/p/los-cocos/
#
'''Implementation of `TiledAction` actions
'''
__docformat__ = 'restructuredtext'

import random
from cocos.euclid import *
from basegrid_actions import *

rr = random.randrange

__all__ = [
           'ShakyTiles',
           'ShatteredTiles',
           'ShuffleTiles',
           'FadeOutTiles',
           ]

# Don't export this class
class Tile(object):
    def __init__(self, position=(0,0), start_position=(0,0), delta=(0,0) ):
        super(Tile,self).__init__()
        self.position = position
        self.start_position = start_position
        self.delta = delta

    def __repr__(self):
        return "(start_pos: %s  pos: %s   delta:%s)" % (self.start_position, self.position, self.delta)

class ShakyTiles( TiledGridAction ):
    '''ShakyTiles simulates a shaky floor composed of tiles

       scene.do( ShakyTiles( randrange=6, grid=(4,4), duration=10) )
    '''

    def init( self, randrange=6, *args, **kw ):
        '''
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange( -randrange, randrange) to do the effect
        '''
        super(ShakyTiles,self).init(*args,**kw)
        self.randrange = randrange

    def update( self, t ):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                for k in range(0,4):

                    idx = (i * 4 * self.grid.y + j * 4 + k) * 2
                    x = self.target.grid.vertex_points[idx]
                    y = self.target.grid.vertex_points[idx+1]

                    x += rr(-self.randrange, self.randrange)
                    y += rr(-self.randrange, self.randrange)

                    self.target.grid.vertex_list.vertices[idx] = int(x)
                    self.target.grid.vertex_list.vertices[idx+1] = int(y)
                
    def __reversed__(self):
        # self
        return ShakyTiles( randrange=self.randrange, grid=self.grid, y_quads=self.grid.y, duration=self.duration)

class ShatteredTiles( TiledGridAction ):
    '''ShatterTiles shatters the tiles according to a random value.
    It is similar to shakes (see `ShakyTiles`) the tiles just one frame, and then continue with
    that state for duration time.
    '''

    def init( self, randrange=6, *args, **kw ):
        '''
        :Parameters:
            `randrange` : int
                Number that will be used in random.randrange( -randrange, randrange) to do the effect
        '''
        super(ShatteredTiles,self).init(*args,**kw)
        self.randrange = randrange
        self._once = False

    def update( self, t ):
        if not self._once:
            for i in range(0, self.grid.x):
                for j in range(0, self.grid.y):
                    for k in range(0,4):
    
                        idx = (i * 4 * self.grid.y + j * 4 + k) * 2
                        x = self.target.grid.vertex_points[idx]
                        y = self.target.grid.vertex_points[idx+1]
    
                        x += rr(-self.randrange, self.randrange)
                        y += rr(-self.randrange, self.randrange)
    
                        self.target.grid.vertex_list.vertices[idx] = int(x)
                        self.target.grid.vertex_list.vertices[idx+1] = int(y)
            self._once = True
                
    def __reversed__(self):
        # Reverse(Shattered) == Normal Tiles
        return ShatteredTiles( randrange=0, grid=self.grid, duration=self.duration)

class ShuffleTiles( TiledGridAction ):
    '''ShuffleTiles moves the tiles randomly across the screen and then put
    them back into the original place.
       scene.do( ShuffleTiles( grid=(4,4), duration=10) )
    '''

    def start(self):
        super(ShuffleTiles,self).start()
        self.tiles = {}
        self.dst_tiles = {}
        self._once = False
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                self.tiles[(i,j)] = Tile( position = Point2(i,j), 
                                          start_position = Point2(i,j), 
                                          delta= self._get_delta(i,j) )

        
    def place_tile(self, i, j):
        t = self.tiles[(i,j)]

        for k in range(0,4):
            idx = (i * 4 * self.grid.y + j * 4 + k) * 2

            x=0
            y=0
            
            if k==1 or k==2:
                x = self.target.grid.x_step
            if k==2 or k==3:
                y = self.target.grid.y_step
                
            x += t.position.x * self.target.grid.x_step
            y += t.position.y * self.target.grid.y_step
            
            self.target.grid.vertex_list.vertices[idx] = int(x)
            self.target.grid.vertex_list.vertices[idx+1] = int(y)
        
    def update( self, t ):
        if t < 1.0/3:
            self.phase_shuffle(t/ (1.0/3) )
        elif t < 2.0/3:
            if self._once is False:
                self.phase_shuffle(1)
                self._once = True
        else:
            self.phase_shuffle_back( (t-2.0/3) / (1.0/3) )

    def phase_shuffle(self, t ):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                self.tiles[(i,j)].position = self.tiles[(i,j)].start_position + self.tiles[(i,j)].delta * t
                self.place_tile(i,j)
   
    def phase_shuffle_back(self, t):
        for i in range(0, self.grid.x):
            for j in range(0, self.grid.y):
                self.tiles[(i,j)].position = self.tiles[(i,j)].start_position + self.tiles[(i,j)].delta * (1-t)
                self.place_tile(i,j)                
                
    # private method
    def _get_delta(self, x, y):
        a = rr(0, self.grid.x), rr(0, self.grid.y)  
        if not self.dst_tiles.get(a, False):
            self.dst_tiles[ a ] = True
            return Point2(*a)-Point2(x,y)
        for i in range(a[0], self.grid.x):
            for j in range(self.grid.y):
                if not self.dst_tiles.get( (i,j), False):
                    self.dst_tiles[ (i,j) ] = True
                    return Point2(i,j)-Point2(x,y)
        for i in range(a[0]):
            for j in range(self.grid.y):
                if not self.dst_tiles.get( (i,j), False):
                    self.dst_tiles[ (i,j) ] = True
                    return Point2(i,j)-Point2(x,y)
        raise GridException("_get_delta() error")

    def __reversed__(self):
        # revere is self, since it will perform the same action
        return ShuffleTiles( grid=self.grid, duration=self.duration)


class FadeOutTiles( TiledGridAction ):
    '''FadeOutTiles fades out each tile following a diagonal path until all the tiles are faded out.
       scene.do( FadeOutTiles( grid=(16,16), duration=10) )
    '''

    def start(self):
        super(FadeOutTiles,self).start()
        self.tiles = {}
        self.dst_tiles = {}
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                self.tiles[(i,j)] = Tile( position = Point2(i,j), 
                                          start_position = Point2(i,j), 
                                          delta=Point2(0,-j) )

    def update( self, t ):
        x,y = t * self.grid
                
        # direction right - up
        for i in range(self.grid.x):
            for j in range(self.grid.y):
                if i+j <= x+y+8:
                    for k in range(0,4):
                        idx =     (i * 4 * self.grid.y + j * 4 + k) * 2
                        idx_dst = (i * 4 * self.grid.y + j * 4 + 2) * 2   # k==2 is coord 'c'

                        vx = self.target.grid.vertex_list.vertices[idx]
                        vy = self.target.grid.vertex_list.vertices[idx+1]
                        
                        x_dst = self.target.grid.vertex_points[idx_dst]
                        y_dst = self.target.grid.vertex_points[idx_dst+1]

                        if k==1 or k==0:    # coord 'a' or 'b'
                            vy = 1 + vy + (y_dst - vy) / 16
                        if k==3 or k==0:    # coord 'a' or 'd'
                            vx = 1 + vx + (x_dst - vx) / 16
                             
                        if vx >= x_dst:
                            vx = x_dst
                        if vy >= y_dst:
                            vy = y_dst
                                
                        self.target.grid.vertex_list.vertices[idx] = int(vx)
                        self.target.grid.vertex_list.vertices[idx+1] = int(vy)
               
    def __reversed__(self):
        raise NotImplementedError('FadeInTiles not implemented yet!')
#        return FadeOutTiles( grid=self.grid, duration=self.duration)
