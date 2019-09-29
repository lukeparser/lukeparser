from luke.themes.baseinstaller import BaseInstaller, install_resources
import os


resources = {
    "bootstrap": {
        "src": "https://github.com/twbs/bootstrap/releases/download/v{version}/bootstrap-{version}-dist.zip",
        "version": "4.1.3"
    },
    "jQuery": {
        "src": "https://code.jquery.com/jquery-{version}.min.js",
        "version": "3.3.1"
    },
    "Popper": {
        "src": "https://cdnjs.cloudflare.com/ajax/libs/popper.js/{version}/esm/popper.min.js",
        "version": "1.15.0"
    },
    "Highlight_js": {
        "src": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{version}/highlight.min.js",
        "version": "9.13.1"
    },
    "Highlight_css": {
        "src": "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/{version}/styles/default.min.css",
        "version": "9.13.1"
    },
    "MathJax": {
        "src": "https://github.com/mathjax/MathJax/archive/{version}.zip",
        "version": "2.7.5"
    },
}


class Installer(BaseInstaller):
    def install(theme_path, theme_name="bootstrap"):
        install_resources(resources, theme_path, theme_name)

