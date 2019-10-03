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
    "robotofont": {
        "src": "https://dl.dafont.com/dl/?f=roboto",
        "version": "current",
        "type": "zip",
        "skipBaseFolder": 0,
        "zip_paths": {
            "css": {
                "ignore": True
            }
        },
        "cdn_paths": {
            "css": {
                "href": "https://fonts.googleapis.com/css?family=Roboto:300,300i,400,400i,500,500i&display=swap",
                "tag": "link",
                "rel": "stylesheet"
            }
        }
    },
    "vctheme": {
        "pkg": "luke.themes.html.vctheme",
        "src": "resources/css/vctheme.css"
    }
}

class Theme(BaseTheme):
    pass
Theme.resources = {**bootstrap_resources,**resources}
