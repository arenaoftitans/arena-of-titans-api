################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################

import re
import signal
import sys
from subprocess import Popen  # noqa: B404 (Popen can be a security risk)

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .run import cleanup


class AotEventHandler(FileSystemEventHandler):
    '''Inspired by RegexMatchingEventHandler.

    https://github.com/gorakhargosh/watchdog/blob/d7ceb7ddd48037f6d04ab37297a63116655926d9/src/watchdog/events.py#L457.
    '''

    IGNORE_REGEXES = [re.compile(r'.*test.*'), re.compile(r'.*__pycache__.*')]
    EVENT_TYPE_MOVED = 'moved'
    EVENT_TYPE_DELETED = 'deleted'
    EVENT_TYPE_CREATED = 'created'
    EVENT_TYPE_MODIFIED = 'modified'

    def __init__(self):
        super().__init__()
        self._loop = None

    def dispatch(self, event):
        paths = []
        if hasattr(event, 'dest_path'):
            paths.append(event.dest_path)
        if event.src_path:
            paths.append(event.src_path)

        if any(r.match(p) for r in self.IGNORE_REGEXES for p in paths):
            return
        else:
            self.on_any_event(event)
            _method_map = {
                self.EVENT_TYPE_MODIFIED: self.on_modified,
                self.EVENT_TYPE_MOVED: self.on_moved,
                self.EVENT_TYPE_CREATED: self.on_created,
                self.EVENT_TYPE_DELETED: self.on_deleted,
            }
            event_type = event.event_type
            _method_map[event_type](event)

    def on_any_event(self, event):
        super().on_any_event(event)
        print('Reload: start', file=sys.stderr)  # noqa: T001
        self.stop_app()
        self.start_app()
        print('Reload: done', file=sys.stderr)  # noqa: T001

    def start_app(self):
        self.app = Popen([  # noqa: B603,B607 (Popen usage)
            'python3',
            '-m', 'aot',
            '--debug',
            '--version', 'latest',
            '--env', 'dev',
        ])

    def stop_app(self):
        self.app.terminate()
        cleanup(None, None)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, loop):
        self._loop = loop


def run_reload():
    aot_event_handler = AotEventHandler()
    aot_event_handler.start_app()
    observer = Observer()
    observer.schedule(aot_event_handler, 'aot', recursive=True)
    observer.start()
    # Make dependent thread shutdown on SIGTERM.
    # This is required for the container to stop with the 0 status code.
    signal.signal(signal.SIGTERM, lambda *args: observer.stop())

    try:
        observer.join()
    except KeyboardInterrupt:
        pass
    finally:
        aot_event_handler.stop_app()
        observer.stop()
    observer.join()
