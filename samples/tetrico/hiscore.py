from __future__ import division, print_function, unicode_literals

#
# HiScore
#

__all__ = ['hiscore']

class HiScoreData( object ):

    POINTS, NAME, LVL = range(3)

    HISCORE_FILENAME = 'hi_scores.txt'

    MAX = 10

    def __init__( self ):
        super(HiScoreData, self).__init__()

        self.load()

    def load(self):
        self.hi_scores = []
        try:
            f = open(self.HISCORE_FILENAME)
            for line in f.readlines():
                # ignore comments
                if line.startswith("#"):
                    continue
                (score,name,lvl) = line.split(',')
                self.hi_scores.append( (int(score),name,int(lvl) ) )
            f.close()
        except IOError:
            # file not found, no problem
            pass

    def save(self):
        try:
            f = open(self.HISCORE_FILENAME,'w')
            for i in self.hi_scores:
                f.write('%d,%s,%d\n' % ( i[0],i[1],i[2] ) )
            f.close()
        except Exception as e:
            print('Could not save hi scores')
            print(e)

    def add( self, score, name, lvl):
        # safe replacement
        for l in name:
            if not l.isalnum():
                name = name.replace(l,'_')

        self.hi_scores.append( (int(score),name,int(lvl) ) )
        self.hi_scores.sort()
        self.hi_scores.reverse()

        self.hi_scores = self.hi_scores[:self.MAX]

        self.save()

    def is_in( self, score ):
        if len( self.hi_scores) < self.MAX:
            return True
        if score > self.hi_scores[-1][0]:
            return True
        return False

    def get( self, max=10 ):
        # only return the max first records
        return self.hi_scores[:max]

hiscore = HiScoreData()
