from __future__ import division, print_function, unicode_literals

__all__ = [ 'status' ]

class Status( object ):
    def __init__( self ):

        # current score
        self.score = 0

        # next piece
        self.next_piece = None

        # current level
        self.level = None

        # current level idx
        self.level_idx = None

        # level lines completed
        self.lines = 0

        # total lines completed
        self.tot_lines = 0

    def reset( self ):
        self.score = 0
        self.next_piece = None
        self.level = None
        self.level_idx = None
        self.lines = 0
        self.tot_lines = 0

status = Status()
