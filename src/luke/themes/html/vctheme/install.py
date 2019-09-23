from luke.themes.baseinstaller import BaseInstaller, downloadZipTo, downloadFileTo, getOrCreateVersionFile, pkgfileTo
import os
from luke.themes.html.bootstrap.install import Installer as BootstrapInstaller



class Installer(BaseInstaller):

    def install(theme_path,theme_name="vctheme"):
        BaseInstaller.install(theme_path,theme_name)
        BootstrapInstaller.install(theme_path,theme_name)
        theme_path = os.path.join(theme_path,theme_name)

        def download_openiconic(version):
            dest = os.path.join(theme_path,"resources","openiconic")
            print("Installing 'openiconic' to '"+dest+"'")
            downloadZipTo("https://github.com/iconic/open-iconic/archive/master.zip", dest)
        version_file = os.path.join(theme_path,"version_openiconic")
        getOrCreateVersionFile(version_file, "current", download_openiconic)

        def download_robotofont(version):
            dest = os.path.join(theme_path,"resources","fonts")
            print("Installing 'robotofont' to '"+dest+"'")
            downloadZipTo("https://dl.dafont.com/dl/?f=roboto", dest, skipBaseFolder=0)
        version_file = os.path.join(theme_path,"version_robotofont")
        getOrCreateVersionFile(version_file, "current", download_robotofont)

        pkgfileTo(("luke.themes.html.vctheme","resources/css/custom.css"),os.path.join(theme_path,"resources","vcstyle.css"))



