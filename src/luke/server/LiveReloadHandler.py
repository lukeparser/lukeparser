from livereload.handlers import LiveReloadHandler as _LiveReloadHandler
import tornado
from tornado import escape
from tornado.util import ObjectDict
import logging
logger = logging.getLogger('livereload-lukeserver')
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from tornado import gen
import asyncio

class ReloadOnFileChange(FileSystemEventHandler):
    def __init__(self,livereload,abspath,url):
        self.livereload = livereload
        self.abspath = abspath
        self.url = url

    def on_modified(self, event):
        if event.src_path == self.abspath:
            msg = {
                'command': 'reload',
                'path': event.src_path,
                'liveCSS': False,
                'liveImg': True,
            }
            self.livereload.send_message(msg)

class AsyncObserver(Observer):
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        super().run()


class LiveReloadHandler(_LiveReloadHandler):
    def on_message(self, message):
        """Handshake with livereload.js
        1. client send 'hello'
        2. server reply 'hello'
        3. client send 'info'
        """
        message = ObjectDict(escape.json_decode(message))
        if message.command == 'hello':
            handshake = {
                'command': 'hello',
                'protocols': [
                    'http://livereload.com/protocols/official-7',
                ],
                'serverName': 'livereload-lukeparser',
            }
            self.send_message(handshake)

        if message.command == 'info' and 'url' in message:
            logger.info('Browser Connected: %s' % message.url)
            url = message["url"]
            abspath = "/".join(url.split("/")[3:]).split("#")[0]
            self._watch_file(abspath,url)

    def on_close(self):
        logger.info('Browser Disconnected')
        self.observer.stop()

    def _watch_file(self,abspath,url):
        if url.endswith("/"):
            abspath += "index.md"
            url += "index.md"
        logger.info("Watching file changes for: "+abspath)
        abspath = os.path.realpath(abspath)
        event_handler = ReloadOnFileChange(self, abspath, url)
        logger.info(abspath)
        self.observer = AsyncObserver()
        self.observer.schedule(event_handler, path=os.path.dirname(abspath), recursive=False)
        try:
            self.observer.start()
        except OSError:
            logger.error('Cannot start observer')
            self.close()
            return


