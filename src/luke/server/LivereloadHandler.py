from luke.server.HTTPWebSocketsHandler import HTTPWebSocketsHandler
import pkgutil
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import urllib


livereload_protocols = [
    "http://livereload.com/protocols/official-7",
    "http://livereload.com/protocols/official-8",
    "http://livereload.com/protocols/official-9"
]

class MyHandler(FileSystemEventHandler):
    def __init__(self,livereload,abspath,url):
        self.livereload = livereload
        self.abspath = abspath
        self.url = url

    def on_modified(self, event):
        if event.src_path == self.abspath:
            self.livereload.livereload_now(self.url)


class LivereloadHandler(HTTPWebSocketsHandler):

    def get_abspath(self,path):
        return path

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def remap_abspath(self,abspath):
        return abspath

    def do_GET(self):
        if self.path.startswith("/livereload.js"):
            self.send_response(200)
            self.send_header("Content-type","application/javascript")
            self.end_headers()
            livereloadjs = pkgutil.get_data("luke.server","livereload.js")
            self.wfile.write(livereloadjs)
        elif self.path.startswith("/livereload"):
            super().do_GET()

    def on_ws_message(self, message):
        message = json.loads(message)
        if message["command"] == "hello":
            protocols = list(set(message["protocols"]).intersection(set(livereload_protocols)))
            if len(protocols) == 0:
                print("no intersecting livereload protocol found. closing connection")
                self._ws_close()
                return
            protocol = sorted(protocols)[-1]

        elif message["command"] == "info":
            url = message["url"]
            url = urllib.parse.unquote(url)
            abspath = self.get_abspath("/"+"/".join(url.split("/")[3:]).split("#")[0])
            abspath = self.remap_abspath(abspath)
            self._watch_file(abspath,url)

        self.log_message('websocket received "%s"',str(message))

    def _watch_file(self,abspath,url):
        if url.endswith("/"):
            abspath += "index.md"
            url += "index.md"
        print("Watching file changes for: ",abspath,url)
        abspath = os.path.realpath(abspath)
        event_handler = MyHandler(self, abspath, url)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=os.path.dirname(abspath), recursive=False)
        self.observer.start()

    def livereload_now(self,url):
        self.send_message(json.dumps({
            "command": 'reload',
            "path": url,
            "liveCSS": True
        }))

    def livereload_alert(self):
        self.send_message(json.dumps({
            "command":"alert",
            "message":"HEY!"
        }).encode("utf-8"))

    def on_ws_connected(self):
        self.send_message(json.dumps({
            "command": "hello",
            "protocols": livereload_protocols,
            "serverName": "Lukeparser"
        }))
        self.log_message('%s','websocket connected')

    def on_ws_closed(self):
        if hasattr(self,"observer"):
            self.observer.stop()
        self.log_message('%s','websocket closed')

    def injectIntoHTML(self,html,hostPort):
        script = '<script type="text/javascript">(function(){ var s=document.createElement("script"); var port=%s; s.src="//"+window.location.hostname+":"+port + "/livereload.js?port=" + port; document.head.appendChild(s); })();</script>' % hostPort
        return html.replace("</head>",script+"</head>")


