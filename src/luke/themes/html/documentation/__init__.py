from luke.themes.html.bootstrap import resources as bootstrap_resources
from luke.themes.basetheme import BaseTheme
import os

resources = {
    "openiconic": {
        "src": "https://github.com/iconic/open-iconic/archive/master.zip",
        "version": "current",
        "zip_paths": {
            "bootstrap_css": "font/css/open-iconic-bootstrap.css"
        },
        "cdn_paths": {
            "bootstrap_css": "https://cdnjs.cloudflare.com/ajax/libs/open-iconic/1.1.1/font/css/open-iconic-bootstrap.min.css"
        }
    },
    "docs": {
        "pkg": "luke.themes.html.documentation",
        "src": "resources/docs.css"
    }
}

class Theme(BaseTheme):

    @classmethod
    def preparse(cls, tree):

        # prepend default components
        prepend = [

            # left
            {"content": [ [ { "arguments": [ [ { "content": [ [ { "command": "listdocuments", "nargs": [], "nested": True, "type": "command", "walk_only_current_dir": True, "basepath": [{"command":"basepath","type":"placeholder"},'/../'] } ] ], "level": "\t", "type": "indent" } ] ], "command": "component", "nargs": [ "left" ], "type": "command" } ] ], "type": "paragraph" },

            # right
            { "content": [ [ { "arguments": [ [ { "content": [ [ { "command": "contentlist", "nargs": [], "nested": True, "type": "command" } ] ], "level": "\t", "type": "indent" } ] ], "command": "component", "nargs": [ "right" ], "type": "command" } ] ], "type": "paragraph" }
        ]

        tree["content"] = prepend + tree["content"]
        return tree

    @classmethod
    def postparse(cls, global_scope):
        if "topleft" in global_scope["components"]:
            topleft = global_scope["components"]["topleft"]

            topleft = topleft.replace("<li ","<li class=\"nav-item\" ")
            # topleft = topleft.replace("<ul ","<ul class=\"navbar-nav bd-navbar-nav flex-row\" ")
            topleft = topleft.replace("<ul ","<ul class=\"navbar-nav bd-navbar-nav flex-row\" ")
            topleft = topleft.replace("<a ","<a class=\"nav-link\" ")
            global_scope["components"]["topleft"] = topleft

        if "topright" in global_scope["components"]:
            topright = global_scope["components"]["topright"]

            topright = topright.replace("<li ","<li class=\"nav-item\" ")
            # topright = topright.replace("<ul ","<ul class=\"navbar-nav bd-navbar-nav flex-row\" ")
            topright = topright.replace("<ul ","<ul class=\"navbar-nav flex-row ml-md-auto d-none d-md-flex\" ")
            topright = topright.replace("<a ","<a class=\"nav-link\" ")
            global_scope["components"]["topright"] = topright

        return global_scope

Theme.resources = {**bootstrap_resources,**resources}
