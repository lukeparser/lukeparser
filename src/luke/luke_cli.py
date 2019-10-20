import sys
import os
from luke.luke import *
import argparse
from pathlib import Path
from luke.defaults import defaults
from luke import __version__


def main(developer_mode=False):

    # =============== #
    # parse arguments #
    # =============== #

    class ArgumentParserWithHelp(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = ArgumentParserWithHelp(description="Lukeparser - the Theme of Markdown with the power of LaTeX.",
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog="""
Example useage:

  List available Themes:
  luke --list

  Run for arbitrary number of files:
  luke my_file_1.md my_file_2.md my_file_3.py

  Run for mutliple themes: (themes can be placed into ~/.config/lukeparser/themes/)
  luke -s bootstrap_cdn.html -s email.html file.md
""")
    parser.add_argument("input", nargs="*", help="input file(s) or folder", default=[])

    # commands (these start other scripts)
    parser.add_argument("--version", action="store_true", default=False,
                        help="Show version information.")
    parser.add_argument("--list", action="store_true", default=False,
                        help="List available themes, languages (filetypes to parse from)"
                             " and views (filetypes to parse to)")
    parser.add_argument("--live", action="store_true", default=False,
                        help="Watch for file change.")
    parser.add_argument("--doc","--documentation", action="store_true", default=False,
                        help="Show the documentation of luke using a live-instance.")
    parser.add_argument("--install", nargs=1,
                        help="Install theme.")
    parser.add_argument("--init", action="store_true", default=False, # TODO: move to pip-install skript?
                        help="Initialize lukeparser. (Create default config-file, install vc_theme).")

    # normal useage
    parser.add_argument("-o", "--output", default=".",
                        help="Folder/Filename(s) of output. (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="count", default=1,
                        help="Available verbosity-levels: 1: luke-verbosity, 2: additional pybison-verbosity")
    parser.add_argument("-l", "--language", default="markdown",
                        help="Language/Parser to use. (default: %(default)s)")

    # theme/resource
    parser.add_argument("-t", "--theme", default=[], action="append",
                        help="Theme(s) to use. Insert path to use custom theme.")
    parser.add_argument("--overwrite-theme", dest="overwrite_theme", action="store_true", default=False,
                        help="Do not allow the theme-choice overloaded by the in-file settings.")

    # resource
    parser.add_argument("--resources-dest", dest="resources_dest", default=None,
                        help="Copy resources to RESOURCE_DEST (if does not exist there).")
    parser.add_argument("--resources-relative", dest="resources_relative", default=None,
                        help="Relative resource-directory from the files directory.")
    # resource shorthands
    parser.add_argument("--resources-here", dest="resources_here", action="store_true", default=False,
                        help="Shorthand: Store resources in working directory."
                             " (Sets resources_dest to working directory)")
    parser.add_argument("--resources-with-file", dest="resources_with_file", action="store_true", default=False,
                        help="Store resources near file. (Sets resources_dest to file directory)")
    parser.add_argument('--copy-resources', dest='copy_resources', action='store_true',
                        help="Copy resource-folder (to resource-dest). (default: %(default)s)")
    parser.add_argument('--no-copy-resources', dest='copy_resources', action='store_false')
    parser.add_argument('--cdn', dest='cdn', action='store_true', default=True,
                        help="Use CDN instead of local resources. (default: %(default)s)")
    parser.add_argument('--no-cdn', dest='cdn', action='store_false')


    # shorthands
    parser.add_argument('--out-here', action='store_true', default=False,
                        help="Save resulting file(s) to current directory. (default: %(default)s)")

    # debugging & internal
    parser.add_argument("--debug", action="store_true", default=False,
                        help="Debug things. (default: %(default)s)")
    parser.add_argument('--keepfiles', dest='keepfiles', action='store_true',
                        help="Keep intermediate files. (default: %(default)s)")
    parser.add_argument('--no-keepfiles', dest='keepfiles', action='store_false')
    parser.set_defaults(keepfiles=False)

    args = parser.parse_args()

    # ============== #
    # parse commands #
    # ============== #


    # list all available languages and views
    if args.version:
        print("Lukeparser "+str(__version__))
        sys.exit(0)

    # list all available languages and views
    if args.list:

        languages = listLanguages()
        themes = listThemes()

        avail_lang = "Available languages / input filetypes:\n\t- " + "\n\t- ".join(
            languages
        )
        avail_themes = "Available views / themes (format: view.theme):\n\t- " + "\n\t- ".join(
            [s[0]+" (preinstalled)" if s[1] == "preinstalled" else s[0]+" ("+s[1]+")" for s in themes]
        )

        print("\n\n".join([avail_lang, avail_themes]))
        sys.exit(0)

    # install a given theme
    if args.install:
        installTheme(args.install[0], reinstall=True)
        sys.exit(0)

    # initialize lukeparser (create config-file, install vc_theme)
    if args.init:
        # TODO create config-file
        # TODO install default theme from config file
        installTheme("vctheme", reinstall=True)
        installTheme("bootstrap", reinstall=True)
        installTheme("documentation", reinstall=True)
        sys.exit(0)

    # start luke-server
    if args.doc:
        from luke.luke_server import main as start_server
        # if developer_mode:
        #     package_dir = os.path.join(luke.__path__[0],"..")
        # else:
        #     package_dir = luke.__path__[0]
        package_dir = luke.__path__[0]
        doc_dir = os.path.join(package_dir,"docs")
        start_server(doc_dir,livereload=False)
        sys.exit(0)

    if args.live:
        from luke.luke_server import main as start_server
        start_server(".")
        sys.exit(0)



    # ============== #
    # parse settings #
    # ============== #

    # if no input is given, nothing can be done
    if len(args.input) == 0:
        parser.print_help()
        print()
        print("Error: Nothing to do. Did you forget to specify a file or folder?")
        sys.exit(1)

    # if no theme is given, use default theme
    if len(args.theme) == 0:
        args.theme.append(defaults["default_theme"])

    # get views and theme-objects
    fetch_themes_and_views(args.theme)

    # import parser & preprocessing
    from luke.Preprocessing import Preprocessing
    _parser = __import__("luke.parser." + args.language, fromlist=['']).Parser
    parser = _parser(verbose=args.verbose > 1, debug=args.debug, keepfiles=args.keepfiles)
    prep = Preprocessing()

    # get current cli-settings
    settings = vars(args)

    # ========== #
    # parse it ! #
    # ========== #

    for file in args.input:
        f = Path(file)
        if f.is_file():
            tree = parse_lang(parser, prep, str(f), **settings)
            apply_views(tree, args.theme, str(f), **settings)
        elif f.is_dir():
            process_dir(f,parser,prep,**settings)
        else:
            raise FileNotFoundError(file)

    # # use stdin / stdout if no input is given
    # # TODO
    # if len(args.input) == 0:
    #     import sys
    #     print("listening for input ... ")
    #     print()
    #     # with open("resources/header.html", "r") as header:
    #     #     header_src = header.read().encode('utf-8')
    #     # with open("resources/footer.html", "r") as footer:
    #     #     footer_src = footer.read().encode('utf-8')

    #     # run
    #     for data in sys.stdin:
    #         # snd = parser.run(read=io.StringIO(data).read)
    #         # sec_levels, sec_tree = prepro.run(snd)
    #         # _, sec_tree = prepro.nest_sections(sec_tree, sec_levels)
    #         # output = html.run(sec_tree)
    #         # print(output.encode("utf-8"))
    #         # sys.stdout.write(output)
    #         sys.stdout.write(data)
    #         sys.stdout.flush()
    #         print(data)


if __name__ == '__main__':
    main()
