import sys
import os
import time
import tornado.ioloop
import tornado.web
import logging
import asyncio
from luke.defaults import defaults
from luke.luke import installTheme
from livereload.server import LiveReloadJSHandler, ForceReloadHandler
from luke.server.LiveReloadHandler import LiveReloadHandler
from luke.server.MarkdownHandler import MarkdownHandler

# settings
logger = logging.getLogger('lukeserver')
hostName = os.environ.get("hostname") or "localhost"
hostPort = int(os.environ.get("hostport") or 8080)
verbose = os.environ.get("verbose") or True
root_dir = os.environ.get("root_dir") or "."
resource_path = os.environ.get("resource_path") or defaults["theme_path"]
resources_relative = os.environ.get("resources_relative") or "lukestyles"
standalone = os.environ.get("standalone") or "true"
livereload = os.environ.get("livereload") or "true"
livereload = livereload.lower() in ("true","yes","t","1")
defaults["theme_path"] = resource_path

# set defaults
parse_settings_default = {
    "verbose": True,
    "resource_path": resource_path,
    "resources_relative": "/"+resources_relative,
    "resources_relative_append_theme": True,
    "theme_name": "vctheme",
}


installTheme(parse_settings_default["theme_name"])







def make_app(root_dir, livereload=True):
    tornado.log.enable_pretty_logging()

    if standalone:
        md_settings = {'path': root_dir, 'default_filename': 'index.md', "parse_settings": parse_settings_default, "injectLivereload": livereload}
        handlers = [
            ('/'+resources_relative+'/(.*)', tornado.web.StaticFileHandler, {'path': resource_path, 'default_filename': ''}),
            ('/()', MarkdownHandler,   md_settings),
            ('/(.*)/', MarkdownHandler, md_settings),
            ('/(.*\.md)', MarkdownHandler, md_settings),
            ('/(.*)', tornado.web.StaticFileHandler, {'path': root_dir, 'default_filename': ''}),
        ]
    else:
        handlers = [
            ('/(.*\.md)', MarkdownHandler)
        ]

    if livereload:
        live_handlers = [
            (r'/livereload', LiveReloadHandler),
            (r'/forcereload', ForceReloadHandler),
            (r'/livereload.js', LiveReloadJSHandler)
        ]
        handlers = live_handlers + handlers

    return tornado.web.Application(handlers)


def main(root_dir=root_dir, livereload=livereload):
    if os.name == "nt" and sys.version_info >= (3,8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    globals()["root_dir"] = root_dir

    if livereload:
        logger.info("Listening for livereload.")

    logger.info(hostName, ":"+str(hostPort))
    if verbose:
        logger.info("verbose mode")
    logger.info("Serving files in "+root_dir)


    logger.info(time.asctime()+ "Server Starts - %s:%s" % (hostName, hostPort))
    app = make_app(root_dir, livereload)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(hostPort, hostName)
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        pass
    logger.info(time.asctime()+ "Server Stops - %s:%s" % (hostName, hostPort))


if __name__ == '__main__':
    main()

