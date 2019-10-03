from luke.themes.html.bootstrap import resources as bootstrap_resources
from luke.themes.basetheme import BaseTheme
import os

resources = {
    "openiconic": {
        "src": "https://github.com/iconic/open-iconic/archive/master.zip",
        "version": "current",
        "zip_paths": {
            "bootstrap_css": "font/css/open-iconic-bootstrap.css"
        }
    },
    "robotofont": {
        "src": "https://dl.dafont.com/dl/?f=roboto",
        "version": "current",
        "type": "zip",
        "skipBaseFolder": 0,
    },
    "vctheme": {
        "pkg": "luke.themes.html.vctheme",
        "src": "resources/css/vctheme.css"
    }
}

class Theme(BaseTheme):
    pass
Theme.resources = {**bootstrap_resources,**resources}
