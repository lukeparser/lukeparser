from luke.themes.html.bootstrap.install import resources as bootstrap_resources
from luke.themes.baseinstaller import BaseInstaller, install_resources
import os

resources = {
    "openiconic": {
        "src": "https://github.com/iconic/open-iconic/archive/master.zip",
        "version": "current"
    },
    "robotofont": {
        "src": "https://dl.dafont.com/dl/?f=roboto",
        "version": "current",
        "type": "zip",
        "skipBaseFolder": 0
    },
    "vctheme": {
        "pkg": "luke.themes.html.vctheme",
        "src": "resources/css/vctheme.css"
    }
}
resources = {**bootstrap_resources,**resources}

class Installer(BaseInstaller):
        def install(theme_path, theme_name="vctheme"):
            install_resources(resources, theme_path, theme_name)

