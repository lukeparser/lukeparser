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
import shutil


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



def fetch_themes_and_views(themes):

    queried_views = []
    for combined_name in themes:

        if not isinstance(combined_name, str):
            queried_views.append(combined_name)
            continue

        theme_name, view_name = parseThemeName(combined_name)

        # get view instance
        try:
            view = __import__("luke.views."+view_name, fromlist=['']).View(
                theme_name=theme_name
            )
        except:
            raise ValueError("The view '"+view_name+"' of your chosen theme '"+combined_name+"' is not known")

        queried_views.append(view)

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
    views = fetch_themes_and_views(themes)

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

        # the view produces the output file
        output = view.run(tree, to_string=to_string, verbose=verbose, **settings)
        outputs.append(output)

        if verbose:
            elapsed = time.time() - t
            print("Time used for applying view: ", "{:.4f}".format(elapsed))

    return outputs

def process_dir(f,parser,prep,**settings_orig):
    settings_orig = {**global_defaults, **settings_orig}
    settings = settings_orig.copy()
    cwd = os.getcwd()
    outname = os.path.basename(f)
    theme = settings["theme"][0]
    if not theme.startswith("documentation") and (theme != "default" or not global_defaults["default_view"].startswith("documentation")):
        raise ValueError("Sorry, processing a whole directory is currently only for the documentation.html theme supported .")
    # TODO: make this code view-specific

    # destination of file (having content)
    if settings["out_here"]:
        path_out = cwd
    else:
        path_out = settings["output"]
    path_out = os.path.join(path_out, outname)


    # set local settings
    # process_dir takes care of these settings
    del settings["input"]
    del settings["output"]
    settings["copy_resources"] = False
    settings["resources_with_file"] = False
    settings["resources_here"] = False
    settings["out_here"] = False
    settings["resources_dest"] = None
    settings["internal_variables"] = {"md_link_replace":"html"}

    # first make a copy of the whole folder
    shutil.copytree(f, path_out)

    # process all files
    for dirName, subdirList, fileList in os.walk(path_out):
        for filename in fileList:
            if not filename.endswith(".md"):
                continue
            filename_path = os.path.join(dirName,filename)

            # destination of resources
            if settings_orig["copy_resources"]:
                if settings_orig["resources_here"]:
                    path_resources_dest = os.path.join(cwd,"luke_resources",theme)
                elif settings_orig["resources_with_file"]:
                    path_resources_dest = os.path.join(path_out,"..","luke_resources",theme)
                else:
                    path_resources_dest = settings_orig["resources_dest"] if settings_orig["resources_dest"] is not None else os.path.join(cwd,"luke_resources",theme)
                path_resources_relative = os.path.relpath(path_resources_dest,os.path.dirname(filename_path))
            else:
                path_resources_dest = None
                if settings_orig["resources_here"]:
                    path_resources_relative = os.path.join(os.path.relpath(cwd,filename_path),"luke_resources",theme)
                elif settings_orig["resources_with_file"]:
                    path_resources_relative = os.path.join("luke_resources",theme)
                elif settings_orig["resources_relative"]:
                    path_resources_relative = settings_orig["resources_relative"]
                else:
                    path_resources_relative = None
            settings["resources_relative"] = path_resources_relative

            tree = parse_lang(parser, prep, filename_path, **settings)
            apply_views(tree, settings["theme"], filename_path, output=filename_path, **settings)

    # copy resource folder if not yet done
    path_theme = os.path.join(settings["theme_path"],"html",theme)
    path_resources_src = os.path.join(settings["theme_path"],"html",theme,"resources")
    if settings_orig["copy_resources"] and not os.path.exists(path_resources_dest):
        if settings_orig["verbose"] >= 1:
            print("Copying resources to: "+path_resources_dest)
        if os.path.exists(path_resources_src):
            shutil.copytree(path_resources_src, path_resources_dest)
        else:
            raise ValueError("The resource-directory '"+path_resources_src+"' does not exist and thus cannot be copied.")



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

