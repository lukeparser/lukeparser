import os

home = os.path.expanduser("~")
config_path = os.path.join(home, ".config","lukeparser")

# set defaults
defaults = {
    "default_theme": "default",
    "default_html_theme": "vctheme",
    "default_reveal_theme": "reveal",
    "default_latex_theme": "basic",
    "default_view": "html",
    "config_path": config_path,
    "theme_path": os.path.join(config_path, "themes"),

    # internal
    "overwrite_theme": False,
    "out_here": False,
    "copy_resources": False,
    "resources_here": False,
    "resources_with_file": False,
    "resources_relative": ".",
    "to_string": False,
    "resources_relative_append_theme": False,
}

