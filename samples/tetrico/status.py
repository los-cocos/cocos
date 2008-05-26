
__all__ = [ 'status' ]

class Status( object ):
    def __init__( self ):
        self.score = 0
        self.next_piece = None
        self.level = None
        self.lines = 0
        self.tot_lines = 0

status = Status()
