import os
import re
import tornado.web
from luke.luke import parse_direct
from luke.parser.markdown import Parser
from luke.views.html import View
from luke.Preprocessing import Preprocessing

class MarkdownHandler(tornado.web.RequestHandler):

    def initialize(self, path: str, default_filename: str = None, view=View, parse_settings: dict = {}, injectLivereload: bool = False) -> None:
        self.root = path
        self.default_filename = default_filename
        self.view = view
        self.parse_settings = parse_settings
        self.injectLivereload = injectLivereload

    def argument_isset(self,name):
        return isinstance(self.get_argument(name,False),str)

    def injectIntoHTML(self,html,hostPort):
        script = '<script type="text/javascript">(function(){ var s=document.createElement("script"); var port=%s; s.src="//"+window.location.hostname+":"+port + "/livereload.js?port=" + port; document.head.appendChild(s); })();</script>' % hostPort
        return html.replace("</head>",script+"</head>")

    async def get(self, path):
        url_path = path

        # check if query is valid
        path = os.path.normpath(path)
        if os.path.join(path, '').startswith(os.path.join('..', '')) or os.path.isabs(path):
            raise tornado.web.HTTPError(403)


        # check if path exists
        path = os.path.join(self.root,path)
        if not os.path.exists(path):
            raise tornado.web.HTTPError(404)

        # helper variables
        isfile = os.path.isfile(path)
        isdir = os.path.isdir(path)
        string_md = None

        # check for default files
        if isdir and self.default_filename != "" and os.path.exists(os.path.join(path, self.default_filename)):
            path = os.path.join(path, self.default_filename)
            isdir = False
            isfile = True

        # parse directories
        if isdir:
            cmd = "list_all" if self.argument_isset("list_all") else "list_md_and_html" if self.argument_isset("list_md_and_html") else "list_md"

            string_md = """
Directory {section-counter=False}
=========================
Settings: [list only markdown](/"""+url_path+") \| [list markdown and html](/"""+url_path+"?list_md_and_html) \| [list all files](/"""+url_path+"?list_all)"

            cmd_append = "" if cmd == "list_md" else "?"+cmd

            string_md += """
            -[action-undo] [**go up**](.."""+cmd_append+""")
            """
            files = [(f+"/", True) if os.path.isdir(os.path.join(path, f)) else (f, False) for f in os.listdir(path)]

            # define filter for listing
            regex = r'.*'
            if cmd == "list_md":
                regex = r'[^.].*(/|(\.md))'
            if cmd == "list_md_and_html":
                regex = r'[^.].*(/|(\.(md|html?)))'

            files = [(f[0], f[1]) for f in files if re.match(regex, f[0])]
            string_md += "\n".join(["-["+("folder" if f[1] else "document")+"] ["+f[0].replace("_", "\\_")+"]("+f[0].replace(")","\\)")+cmd_append+")" for f in files])
            string_md += "\n"

        # parse 404
        elif not isfile:
            string_md = """
**404** -- File not found {section-counter=False}
=========================

Did we miss something?

"""


        parser = Parser()
        prep = Preprocessing()

        self.set_status(200)
        self.set_header("Content-type", "text/html")

        try:
            s = parse_direct(parser, prep, self.view(), to_string=True, file_path=path, string_md=string_md, **self.parse_settings)
            if self.injectLivereload:
                s = s.decode("utf-8")
                s = self.injectIntoHTML(s, "window.location.port")
                s = bytes(s, "utf-8")
            self.write(s)
        except Exception as e:
            string_md = """
*__Exception__ Occured* {section-counter=False}
=================

``` {.card}
"""+str(e)+"""
```
"""
            s = parse_direct(parser, prep, self.view(), to_string=True, file_path=path, string_md=string_md, **self.parse_settings)
            if self.injectLivereload:
                s = s.decode("utf-8")
                s = self.injectIntoHTML(s, "window.location.port")
                s = bytes(s, "utf-8")
            self.write(s)


