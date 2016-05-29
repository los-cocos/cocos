"""original code moved to cocos.scenes.sequences"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import warnings
from cocos.scenes.sequences import SequenceScene as SQ


class SequenceScene(SQ):
    """moved to cocos.scenes.sequences"""
    def __init__(self, *scenes):
        warnings.warn('SequenceScene was moved from cocos.utils to cocos.scenes.sequences; '
                      'The cocos.utils module will be removed in later cocos releases')
        super(SequenceScene, self).__init__(*scenes)
