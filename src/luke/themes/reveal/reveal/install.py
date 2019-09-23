from luke.themes.baseinstaller import BaseInstaller, downloadZipTo, downloadFileTo, getOrCreateVersionFile, pkgfileTo
import os
from luke.themes.html.bootstrap.install import Installer as BootstrapInstaller



class Installer(BaseInstaller):

    def install(theme_path,theme_name="reveal"):
        BaseInstaller.install(theme_path,theme_name)
        theme_path = os.path.join(theme_path,theme_name)

        def download_reveal(version):
            dest = os.path.join(theme_path,"resources")
            print("Installing 'reveal' to '"+dest+"'")
            downloadZipTo("https://github.com/hakimel/reveal.js/archive/master.zip", dest)
        version_file = os.path.join(theme_path,"version_reveal")
        getOrCreateVersionFile(version_file, "current", download_reveal)

        def download_head(version):
            dest = os.path.join(theme_path,"resources","head.min.js")
            print("Installing 'head.js' to '"+dest+"'")
            downloadFileTo("https://cdnjs.cloudflare.com/ajax/libs/headjs/"+version+"/head.min.js",dest)
        version_file = os.path.join(theme_path,"version_headjs")
        getOrCreateVersionFile(version_file, "1.0.3", download_head)

