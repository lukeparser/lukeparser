import time
import json
import os
import importlib
import pkgutil
import luke
import luke.parser
import luke.views
import luke.themes
from luke.defaults import defaults as global_defaults


# inspect available choices
def listLanguages():
    return [modname for importer, modname, ispkg in pkgutil.iter_modules(luke.parser.__path__)]


def listViews():
    return [modname for importer, modname, ispkg in pkgutil.iter_modules(luke.views.__path__) if modname != "View"]


def listThemes():
    views = listViews()
    theme_list = []
    for view in views:

        v = importlib.import_module("luke.views."+view).View()
        theme_list += v.listThemes()

    return theme_list


def installTheme(themename, reinstall=False):
    theme, view = parseThemeName(themename)
    v = importlib.import_module("luke.views."+view).View()
    v.installTheme(theme)


def getDefaultFileOrVar(path,file_or_varname):
    default_file = os.path.join(path, "views", file_or_varname)

    # get default setting first
    default = global_defaults[file_or_varname]

    # overwrite with file contents
    if os.path.exists(default_file):
        with open(default_file, "r") as f:
            default = f.readlines()[0][:-1]

    # for value "default" replace with setting again
    if default == "default":
        default = default[file_or_varname]

    return default


def parseThemeName(combined_name):
    combined_split = combined_name.split(".")
    if len(combined_split) == 1:
        try:
            theme_name, view_name = importlib.import_module("luke.views."+combined_name).default_theme, combined_name
        except:
            theme_name, view_name = combined_name, global_defaults["default_view"]
    else:
        theme_name, view_name = combined_split[0:2]
    return theme_name, view_name


cached_views = {}


def prefetch_themes_and_views(themes):

    queried_views = []
    for combined_name in themes:

        if not isinstance(combined_name, str):
            queried_views.append(combined_name)
            continue

        theme_name, view_name = parseThemeName(combined_name)

        # get view instance
        if view_name not in cached_views:
            try:
                cached_views[view_name] = __import__("luke.views."+view_name, fromlist=['']).View(
                    theme_name=theme_name
                )
            except:
                raise ValueError("The view '"+view_name+"' of your chosen theme '"+combined_name+"' is not known")

        queried_views.append(cached_views[view_name])

    return queried_views


def parse_direct(parser, prep, themes, **settings):
    tree = parse_lang(parser=parser, prep=prep, **settings)
    outputs = apply_views(tree, themes=themes, **settings)
    return outputs[0]


# parser routines
def parse_lang(parser, prep, file_path=None, string_md=None, verbose=False, keepfiles=False, **kwargs):
    # for verbose == False and keepfiles == False this codes collapses to
    #   snd = parser.run(read=io_object.read)
    #   return prep.run(snd, filename=file_path)

    # check parameter correctness
    if file_path is None and string_md is None:
        raise ValueError("Either file_path or string_md has to be given.")

    # helpers
    basename, _ = os.path.splitext(file_path) if string_md is None else ("luke_output", 0)
    outfile_list = basename + ".parsed.json"
    outfile_tree = basename + ".json"

    # ------- #
    # parsing #
    # ------- #
    if verbose:
        print("Parsing '{}'".format("string" if string_md else file_path))

    # parse string or file
    if string_md:
        t = time.time()
        snd = parser.parse_string(string_md)
        parser.reset()
        elapsed = time.time() - t
    else:
        with open(file_path, "r") as otherfile:
            t = time.time()
            snd = parser.run(file=file_path, debug=0)
            parser.reset()
            elapsed = time.time() - t

    if verbose:
        print("Time used for actual parsing: ", "{:.4f}".format(elapsed))

    if keepfiles:
        with open(outfile_list, "w") as jsonfile:
            json.dump(snd, jsonfile, indent=4, sort_keys=True)

    # ------------ #
    # list to tree #
    # ------------ #
    if verbose:
        print("Preprocessing '{}'...".format("string" if string_md else file_path))
        t = time.time()

    # preprocessing: nesting & merging, adding scopes, convert indentation
    tree = prep.run(snd, filename=file_path)

    if verbose:
        print("Time used for preprocessing:", "{:.4f}".format(time.time() - t))

    if keepfiles:
        with open(outfile_tree, 'w') as treefile:
            json.dump(tree, treefile, indent=4, sort_keys=True)

    return tree


def apply_views(tree, themes, file_path, verbose=False, to_string=False, **settings):
    if not isinstance(themes, list):
        themes = [themes]

    # import themes (with corresponding views)
    views = prefetch_themes_and_views(themes)

    # ----------- #
    # apply views #
    # ----------- #
    outputs = []

    # special case: tree is empty
    if not tree:
        return [""*len(views)]

    # apply all views one after another
    for view in views:
        viewname = type(view).__name__

        if verbose:
            print("Applying view '{}'".format(type(view).__name__))
            t = time.time()

        # the view produces no output
        output = view.run(tree, to_string=to_string, verbose=verbose, **settings)
        outputs.append(output)

        if verbose:
            elapsed = time.time() - t
            print("Time used for applying view: ", "{:.4f}".format(elapsed))

    return outputs


# ===============
# example useage:
# ===============

# # init
# from parser.markdown import Parser
# from views.html import View
# from Preprocessing import Preprocessing
# parser = Parser(verbose=0, debug=0)
# prep = Preprocessing()
# view = View()

# # markdown to html
# parse_lang(parser, file)
# apply_view(prep, view, file, themename)

