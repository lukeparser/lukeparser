from luke.themes.baseinstaller import BaseInstaller, install_resources
import os

resources = {
    "reveal": {
        "src": "https://github.com/hakimel/reveal.js/archive/master.zip",
        "version": "current"
    },
    "head": {
        "src": "https://cdnjs.cloudflare.com/ajax/libs/headjs/{version}/head.min.js",
        "version": "1.0.3",
    }
}

class Installer(BaseInstaller):
        def install(theme_path, theme_name="reveal"):
            install_resources(resources, theme_path, theme_name)
