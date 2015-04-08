# ----------------------------------------------------------------------------
# cocos2d
# Copyright (c) 2008-2012 Daniel Moisset, Ricardo Quesada, Rayentray Tappa,
# Lucio Torre
# Copyright (c) 2009-2015  Richard Jones, Claudio Canepa
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
"""
Custom clocks used by cocos to perform special tasks, like:
    - recording a cocos app as a sequence of snapshots with an exact, fixed framerate
    - jump in a predefined sequence of timestamps taking snapshots

dev notes:
There's code duplication here, but having separated codepaths would help to
follow changes in pyglet 1.2dev. When released, we could refactor this with
some confidence.

References to the classes defined here are discouraged in code outside this
module because of possible changes.

The public interface should be
    - get_recorder_clock
    - set_app_clock
"""

from __future__ import division, print_function, unicode_literals

__docformat__ = 'restructuredtext'

import pyglet


def get_recorder_clock(framerate, template, duration=0):
    """
    Returns a clock object suitable to be used as a pyglet app clock, which
    will provide a steady framerate, and saves a snapshot for each frame from
    time=0 to time=duration

    The clock object class depends on the pyglet version, and is set automatically

    :Parameters:
        `framerate` : int
            the number of frames per second
        `template` : str
            snapshot filenames will be template%frame_number (ex: "s%d.png" -> s0.png, s1.png...)
        `duration` : float
            the amount of seconds to record, or 0 for infinite
    """
    if pyglet.version.startswith('1.1'):
        # works with pyglet 1.1.4release
        clock = ScreenReaderClock(framerate, template, duration)
    else:
        # works with pyglet 1.2dev , branch default, 2638:ca17f2a533b7 (2012 04)
        clock = ScreenReaderClock_12dev(framerate, template, duration)
    return clock


def get_autotest_clock(sampler):
    """
    Returns a clock object suitable to be used as a pyglet app clock, which
    will follow a test plan to advance time and take snapshots.

    The clock object class depends on the pyglet version, and is determined automatically.

    :Parameters:
        `sampler` : obj
            obj with interface sampler.next(last_app_time) -> next_app_time
            Drives the app trough the desired states, take snapshots and handles
            the app termination conditions.
    """
    if pyglet.version.startswith('1.1'):
        # works with pyglet 1.1.4release
        clock = AutotestClock(sampler)
    else:
        # works with pyglet 1.2dev , branch default, 2638:ca17f2a533b7 (2012 04)
        clock = AutotestClock_12dev(sampler)
    return clock


def set_app_clock(clock):
    """
    Sets the cocos (or pyglet) app clock to a custom one
    """
    if pyglet.version.startswith('1.1'):
        # works with pyglet 1.1.4release
        pyglet.clock._default = clock
    else:
        # works with pyglet 1.2dev , branch default, 2638:ca17f2a533b7 (2012 04)
        pyglet.app.event_loop.clock = clock
        pyglet.clock._default = clock
        # pyglet.app.base.EventLoop._run_estimated murks the water by accessing
        # the clock's time provider (which is not in sync with our fake time),
        # so use _run instead
        pyglet.app.event_loop._run_estimated = pyglet.app.event_loop._run


class ScreenReaderClock(pyglet.clock.Clock):
    """ Make frames happen every 1/framerate and takes screenshots

        This class is compatible with pyglet 1.1.4release, it is not compatible
        with pyglet 1.2dev
    """

    def __init__(self, framerate, template, duration):
        super(ScreenReaderClock, self).__init__()
        self.framerate = float(framerate)
        self.template = template
        self.duration = duration
        self.frameno = 0
        self.fake_time = 0

    def tick(self, poll=False):
        """Signify that one frame has passed.

        """
        # Code is the same as in baseclass, except changes pointed in comments

        # deleted code for rescheduling the process, we want to do our task
        # the faster possible

        # our payload: take screenshot and handle end of snapshot session
        self._screenshot_logic()

        # update the app time as desired, this replaces ts = self.time()
        ts = self._get_ts()

        # below is the same as in the stock pyglet 1.1.4 clock.Clock.tick
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
            [item for item in self._schedule_interval_items if item.next_ts > ts]

        if need_resort:
            # TODO bubble up changed items might be faster
            self._schedule_interval_items.sort(key=lambda a: a.next_ts)

        return delta_t

    def _screenshot_logic(self):
        """takes screenshots, handles end of screenshot session"""
        # take screenshot
        pyglet.image.get_buffer_manager().get_color_buffer().save(self.template % self.frameno)
        self.frameno += 1

        # end?
        if self.duration:
            if self.fake_time > self.duration:
                raise SystemExit()

    def _get_ts(self):
        """handles the time progression"""
        ts = self.fake_time
        self.fake_time = self.frameno / self.framerate
        return ts


class ScreenReaderClock_12dev(pyglet.clock.Clock):
    """ Make frames happen every 1/framerate and takes screenshots

        This class is compatible with pyglet 1.2dev, it is not compatible
        with pyglet 1.1.4release
    """

    def __init__(self, framerate, template, duration):
        super(ScreenReaderClock_12dev, self).__init__()
        self.framerate = float(framerate)
        self.template = template
        self.duration = duration
        self.frameno = 0
        self.fake_time = 0.0

    def update_time(self):
        """Get the (fake) elapsed time since the last call to `update_time`
            Additionally, take snapshots.

        :rtype: float
        :return: The number of seconds since the last `update_time`, or 0
            if this was the first time it was called.
        """
        # Code is the same as in baseclass, except changes pointed in comments

        # our payload: take screenshot and handle end of snapshot session
        self._screenshot_logic()

        # update the app time as desired, this replaces ts = self.time()
        ts = self._get_ts()

        # below is the same as in the stock pyglet 1.2dev clock.Clock.update_time
        if self.last_ts is None:
            delta_t = 0
        else:
            delta_t = ts - self.last_ts
            self.times.insert(0, delta_t)
            if len(self.times) > self.window_size:
                self.cumulative_time -= self.times.pop()
        self.cumulative_time += delta_t
        self.last_ts = ts

        return delta_t

    def get_sleep_time(self, sleep_idle):
        """sleep time between frames; 0.0 as as we want to run as fast as possible"""
        return 0.0

    def _screenshot_logic(self):
        """takes screenshots, handles end of screenshot session"""
        # take screenshot
        pyglet.image.get_buffer_manager().get_color_buffer().save(self.template % self.frameno)
        self.frameno += 1

        # end?
        if self.duration:
            if self.fake_time > self.duration:
                raise SystemExit()

    def _get_ts(self):
        """handles the time progression"""
        ts = self.fake_time
        self.fake_time = self.frameno/self.framerate
        return ts


class AutotestClock(pyglet.clock.Clock):
    """Make frames follow a test plan

        This class is compatible with pyglet 1.1.4release, it is not compatible
        with pyglet 1.2dev
    """

    def __init__(self, screen_sampler):
        super(AutotestClock, self).__init__()
        self.screen_sampler = screen_sampler

    def tick(self, poll=False):
        # Code is the same as in baseclass, except changes pointed in comments

        # deleted code for rescheduling the process, we want to do our task
        # as fast as possible

        # this was ts = self.time() in pyglet, here .next will  drive the
        # desired fake time, take snapshots, and handle end conditions for
        # the snapshots session
        ts = self.screen_sampler.next(self.last_ts)

        # below is the same as in the stock pyglet 1.1.4 clock.Clock.tick
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
            [item for item in self._schedule_interval_items if item.next_ts > ts]

        if need_resort:
            # TODO bubble up changed items might be faster
            self._schedule_interval_items.sort(key=lambda a: a.next_ts)

        return delta_t

    def get_sleep_time(self, sleep_idle):
        return 0


class AutotestClock_12dev(pyglet.clock.Clock):
    """Make frames follow a test plan

        This class is compatible with pyglet 1.2dev, it is not compatible
        with pyglet 1.1.4release
    """

    def __init__(self, screen_sampler):
        super(AutotestClock_12dev, self).__init__()
        self.screen_sampler = screen_sampler

    def update_time(self):
        """Get the (fake) elapsed time since the last call to `update_time`
            Additionally, take snapshots.

        :rtype: float
        :return: The number of seconds since the last `update_time`, or 0
            if this was the first time it was called.
        """
        # Code is the same as in baseclass, except changes pointed in comments

        # this was ts = self.time() in pyglet, here .next will  drive the
        # desired fake time, take snapshots, and handle end conditions for
        # the snapshots session
        ts = self.screen_sampler.next(self.last_ts)

        # below is the same as in the stock pyglet 1.2dev clock.Clock.update_time
        if self.last_ts is None:
            delta_t = 0
        else:
            delta_t = ts - self.last_ts
            self.times.insert(0, delta_t)
            if len(self.times) > self.window_size:
                self.cumulative_time -= self.times.pop()
        self.cumulative_time += delta_t
        self.last_ts = ts

        return delta_t

    def get_sleep_time(self, sleep_idle):
        """sleep time between frames; 0.0 as as we want to run as fast as possible"""
        return 0.0
