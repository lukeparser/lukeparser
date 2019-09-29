from luke.themes.html.bootstrap.install import resources as bootstrap_resources
from luke.themes.baseinstaller import BaseInstaller, install_resources
import os

resources = {
    "openiconic": {
        "src": "https://github.com/iconic/open-iconic/archive/master.zip",
        "version": "current"
    },
    "docs": {
        "pkg": "luke.themes.html.documentation",
        "src": "resources/docs.css"
    }
}
resources = {**bootstrap_resources,**resources}

class Installer(BaseInstaller):
        def install(theme_path, theme_name="documentation"):
            install_resources(resources, theme_path, theme_name)
