from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import os
from mimetypes import guess_type
import urllib
import re
from luke.defaults import defaults
from luke.luke import installTheme
from luke.server.LivereloadHandler import LivereloadHandler

hostName = os.environ.get("hostname") or "localhost"
hostPort = int(os.environ.get("hostport") or 8080)
verbose = os.environ.get("verbose") or True
root_dir = os.environ.get("root_dir") or "."
resource_path = os.environ.get("resource_path") or defaults["theme_path"]
resources_relative = os.environ.get("resources_relative") or "/lukestyles"
standalone = os.environ.get("standalone") or "true"
livereload = os.environ.get("livereload") or "true"
serve_themes = os.environ.get("serve_themes") or "true"
list_directory = os.environ.get("list_directory") or "true"
list_directory_all = os.environ.get("list_directory_all") or "true"
make_index_mainpage = os.environ.get("make_index_mainpage") or "true"


defaults["theme_path"] = resource_path

from luke.views.html import View
from luke.views.reveal import View as View_Reveal

parse_settings_default = {
    "verbose": True,
    "resource_path": resource_path,
    "resources_relative": resources_relative,
    "resources_relative_append_theme": True,
    "theme_name": "vctheme",
}

file_ending_mapping = {
    ".md": { 
        **parse_settings_default,
        **{"view": View}
    },
    ".reveal": { 
        **parse_settings_default,
        **{"view": View_Reveal,
           "theme_name": "reveal",
            }
    }
}



installTheme(parse_settings_default["theme_name"])


livereload = livereload.lower() in ("true","yes","t","1")

# if livereload:
print("Serving livereload")
baseserver = LivereloadHandler
# else:
#     print("Serving no livereload")
#     baseserver = BaseHTTPRequestHandler

import os
import sys
sys.path.append(os.path.realpath("luke"))
from luke.luke import *
from luke.parser.markdown import Parser
from luke.Preprocessing import Preprocessing


class MyServer(baseserver, object):

    def get_abspath(self, path):
        return os.path.abspath(root_dir + path)

    def remap_abspath(self, abspath):
        for i in file_ending_mapping.keys():
            abspath = abspath.replace(".md"+i, ".md")
        return abspath

    def do_GET(self):
        self.path = urllib.parse.unquote(self.path)
        super(MyServer, self).do_GET()

        # map resources_relative to resource_path
        if standalone == "true" and self.path.startswith(resources_relative):
            relative = self.path[len(resources_relative)+1:].split("?")[0]
            absolute_path_to_resource = os.path.join(resource_path, relative)
            if not os.path.exists(absolute_path_to_resource):
                self.send_response(404)
            else:
                self.send_response(200)
                self.send_header("Content-type", guess_type(absolute_path_to_resource)[0])
                self.end_headers()
                with open(absolute_path_to_resource, "rb") as f:
                    self.wfile.write(f.read())
            return

        # extract command
        path_split = self.path.split("?")
        self.path, cmd = path_split[0], path_split[-1] if len(path_split) > 1 else ""

        # ensure existence of path (or remappings)
        if self.path.endswith("/"):
            file_ext = "/"
        else:
            self.path, file_ext = os.path.splitext(self.path)
            if file_ext == ".md":
                self.path = self.path+".md"
            if file_ext not in file_ending_mapping.keys():
                self.path = self.path+file_ext
        path = self.get_abspath(self.path)
        if os.path.isdir(path) and not path.endswith("/"):
            path = path + "/"
        if not os.path.exists(path) or not path.startswith(os.path.abspath(root_dir)+os.sep):
            self.send_response(404)
            return

        # helper variables
        ismd = file_ext in file_ending_mapping.keys()
        isdir = os.path.isdir(path)
        string_md = None

        if standalone == "true":
            # parse command
            list_directory_all_type = "list_md"
            if cmd in ["list_md", "list_md_and_html", "list_all"]:
                list_directory_all_type = cmd

            # send file directly
            if not isdir and not ismd:
                self.send_response(200)
                mimetype = guess_type(path)[0]
                self.send_header("Content-type", mimetype)
                self.end_headers()
                if mimetype == "text/html":
                    with open(path, "rb") as f:
                        content = f.read().decode("utf-8")
                        content = self.injectIntoHTML(content, hostPort)
                        self.wfile.write(bytes(content, "utf-8"))
                else:
                    with open(path, "rb") as f:
                        self.wfile.write(f.read())
                return

            # parse directories
            if isdir and make_index_mainpage and os.path.exists(os.path.join(path, "index.md")):
                path = os.path.join(path, "index.md")
                isdir = False
                ismd = True

            if isdir and list_directory:
                self_path_escaped = self.path.replace(")", "\\)")
                string_md = """
Directory {section-counter=False}
=========================
Settings: [list only markdown]("""+self_path_escaped+"?list_md) \| [list markdown and html]("""+self_path_escaped+"?list_md_and_html) \| [list all files]("""+self_path_escaped+"?list_all)"

                if list_directory_all == "true":
                    pass
                cmd_append = "" if cmd == "" else "?"+cmd

                string_md += """
                -[action-undo] [**go up**](.."""+cmd_append+""")
                """
                files = [(f+"/", True) if os.path.isdir(os.path.join(path, f)) else (f, False) for f in os.listdir(path)]

                # define filter for listing
                regex = r'.*'
                if list_directory_all == "true":
                    if list_directory_all_type == "list_md":
                        regex = r'[^.].*(/|(\.md))'
                    if list_directory_all_type == "list_md_and_html":
                        regex = r'[^.].*(/|(\.(md|html?)))'

                files = [(f[0], f[1]) for f in files if re.match(regex, f[0])]
                string_md += "\n".join(["-["+("folder" if f[1] else "document")+"] ["+f[0].replace("_", "\\_")+"]("+f[0].replace(")","\\)")+cmd_append+")" for f in files])
                string_md += "\n"

            # parse 404
            elif not ismd:
                string_md = """
**404** -- File not found {section-counter=False}
=========================

Did we miss something?

"""

        # in non-standalone-mode: parse only md files
        elif not ismd:
            self.send_response(404)
            return

        parser = Parser()
        prep = Preprocessing()
        view = file_ending_mapping[file_ext]["view"]() if file_ext in file_ending_mapping.keys() else View()
        parse_settings = file_ending_mapping[file_ext] if file_ext in file_ending_mapping.keys() else file_ending_mapping[".md"]

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        try:
            if livereload:
                # include livereload script
                s = parse_direct(parser, prep, view, to_string=True, file_path=path, string_md=string_md, **parse_settings).decode("utf-8")
                s = self.injectIntoHTML(s, hostPort)
                self.wfile.write(bytes(s, "utf-8"))
            else:
                self.wfile.write(parse_direct(parser, prep, view, to_string=True, file_path=path, string_md=string_md, **parse_settings))
        except Exception as e:
            string_md = """
*__Exception__ Occured* {section-counter=False}
=================

``` {.card}
"""+str(e)+"""
```
"""
            if livereload:
                s = parse_direct(parser, prep, view, to_string=True, file_path=path, string_md=string_md, **parse_settings).decode("utf-8")
                s = self.injectIntoHTML(s, hostPort)
                self.wfile.write(bytes(s, "utf-8"))
            else:
                self.wfile.write(parse_direct(parser, prep, view, to_string=True, file_path=root_dir+self.path, string_md=string_md, **parse_settings))


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass

def main(root_dir=root_dir):
    globals()["root_dir"] = root_dir

    print(hostName, ":", hostPort)
    if verbose:
        print("verbose mode")
    print("Serving files in "+root_dir)


    my_server = ThreadingSimpleServer((hostName, hostPort), MyServer)
    print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass

    my_server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))


if __name__ == '__main__':
    main()

