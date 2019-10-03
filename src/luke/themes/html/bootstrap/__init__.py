from luke.themes.basetheme import BaseTheme
import os


resources = {
    "bootstrap": {
        "src": "https://github.com/twbs/bootstrap/releases/download/v{version}/bootstrap-{version}-dist.zip",
        "version": "4.1.3",
        "zip_paths": {
            "css": "bootstrap.min.css",
            "js": "bootstrap.min.js",
        },
        "cdn_paths": {
            "css": {
                "href": "https://stackpath.bootstrapcdn.com/bootstrap/{version}/css/bootstrap.min.css",
                "rel": "stylesheet",
                "integrity": "sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO",
                "crossorigin":"anonymous"
            },
            "js": {
                "src": "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.bundle.min.js",
                "integrity": "sha384-pjaaA8dDz/5BgdFUPX6M/9SUZv4d12SUPF0axWc+VRZkx5xU3daN+lYb49+Ax+Tl",
                "crossorigin":"anonymous"
            },
        }
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
        "version": "2.7.6",
        "zip_paths": {
            "js": "MathJax.js",
        },
        "cdn_paths": {
            "js": "https://cdnjs.cloudflare.com/ajax/libs/mathjax/{version}/MathJax.js"
        }
    },
}


class Theme(BaseTheme):
    pass
Theme.resources = resources
