import sys
import os
import argparse
from ruamel import yaml
from ruamel.yaml.comments import CommentedMap
yaml.add_representer(dict, lambda self, data: yaml.representer.SafeRepresenter.represent_dict(self, data.items()))

home = os.path.expanduser("~")
config_path = os.path.join(home, ".config","lukeparser")

#    default-dict (here defined)
#         | creates objects
#         v
#    ArgumentParser
#    ConfigParser
#         | - user can overwrite
#         v
#    overwrites defaults-dict
#         | - mode chooses default
#         v
#    build new defaults
#


class D:
    def __init__(self,value,*args,**kwargs):
        self.value = value
        self.argparse = args

    def __str__(self):
        return str(self.value)


defaults = {
    "general": {
        "theme_path": os.path.join(config_path, "themes"),
        "default_theme": {
            "html": "bootstrap",
            "reveal": "reveal",
            "latex": "basic"
        },
        "default_view": "html",

        "cdn": True,
        "overwrite_theme": False,
        "out_here": False,
        "copy_resources": False,
        "resources_here": False,
        "resources_with_file": False,
        "resources_relative": ".",
        "to_string": False,
        "resources_relative_append_theme": D(False,"blub"),
    },
    "cli": {

    },
    "server": {

    },
    "live": {

    },
    "parser": {

    },
}



def make_config_yaml(defaults=defaults,level=0):
    s = ""
    indent = "    "
    for key,val in defaults.items():
        s += indent*level+key +": "
        if isinstance(val,dict):
            s += "\n"+make_config_yaml(val,level+1)
        else:
            s += str(val)+"\n"
    return s


# yaml_text = make_config_yaml(defaults)
# print(yaml_text)
# for testing
# yamlobj = yaml.load(yaml_text,yaml.Loader)#,yaml.RoundTripLoader)
# print(yaml.safe_dump(yamlobj,indent=4))
# import sys
# sys.exit(0)


class ArgumentParserWithHelp(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


