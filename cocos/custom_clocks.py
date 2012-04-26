# cocos2d
# Copyright (c) 2008-2011 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#   * Neither the name of cocos2d nor the names of its
#     contributors may be used to endorse or promote products
#     derived from this software without specific prior written
#     permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------
import pyglet

class ScreenReaderClock(pyglet.clock.Clock):
    ''' Make frames happen every 1/framerate and takes screenshots '''

    def __init__(self, framerate, template, duration):
        super(ScreenReaderClock, self).__init__()
        self.framerate = framerate
        self.template = template
        self.duration = duration
        self.frameno = 0
        self.fake_time = 0

    def tick(self, poll=False):
        '''Signify that one frame has passed.

        '''
        # take screenshot
        pyglet.image.get_buffer_manager().get_color_buffer().save(self.template % (self.frameno) )
        self.frameno += 1

        # end?
        if self.duration:
            if self.fake_time > self.duration:
                raise SystemExit()

        # fake time.time
        ts = self.fake_time
        self.fake_time += 1.0/self.framerate

        if self.last_ts is None:
            delta_t = 0
        else:
            delta_t = ts - self.last_ts
            self.times.insert(0, delta_t)
            if len(self.times) > self.window_size:
                self.cumulative_time -= self.times.pop()
        self.cumulative_time += delta_t
        self.last_ts = ts

        # Call functions scheduled for every frame
        # Dupe list just in case one of the items unchedules itself
        for item in list(self._schedule_items):
            item.func(delta_t, *item.args, **item.kwargs)

        # Call all scheduled interval functions and reschedule for future.
        need_resort = False
        # Dupe list just in case one of the items unchedules itself
        for item in list(self._schedule_interval_items):
            if item.next_ts > ts:
                break
            item.func(ts - item.last_ts, *item.args, **item.kwargs)
            if item.interval:
                # Try to keep timing regular, even if overslept this time;
                # but don't schedule in the past (which could lead to
                # infinitely-worsing error).
                item.next_ts = item.last_ts + item.interval
                item.last_ts = ts
                if item.next_ts <= ts:
                    if ts - item.next_ts < 0.05:
                        # Only missed by a little bit, keep the same schedule
                        item.next_ts = ts + item.interval
                    else:
                        # Missed by heaps, do a soft reschedule to avoid
                        # lumping everything together.
                        item.next_ts = self._get_soft_next_ts(ts, item.interval)
                        # Fake last_ts to avoid repeatedly over-scheduling in
                        # future.  Unfortunately means the next reported dt is
                        # incorrect (looks like interval but actually isn't).
                        item.last_ts = item.next_ts - item.interval
                need_resort = True

        # Remove finished one-shots.
        self._schedule_interval_items = \
            [item for item in self._schedule_interval_items \
             if item.next_ts > ts]

        if need_resort:
            # TODO bubble up changed items might be faster
            self._schedule_interval_items.sort(key=lambda a: a.next_ts)

        return delta_t
