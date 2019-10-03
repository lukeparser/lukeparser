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
    pass
Theme.resources = {**bootstrap_resources,**resources}
