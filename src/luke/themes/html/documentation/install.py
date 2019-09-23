from luke.themes.baseinstaller import BaseInstaller, downloadZipTo, downloadFileTo, getOrCreateVersionFile, pkgfileTo
import os



class Installer(BaseInstaller):

    def install(theme_path,theme_name="documentation"):
        theme_path = os.path.join(theme_path,theme_name)

        # bootstrap
        def download_bootstrap(version):
            dest = os.path.join(theme_path,"resources")
            print("Installing 'Bootstrap' to '"+dest+"'")
            downloadZipTo("https://github.com/twbs/bootstrap/releases/download/v"+version+"/bootstrap-"+version+"-dist.zip", dest)
        version_file = os.path.join(theme_path,"version_bootstrap")
        getOrCreateVersionFile(version_file, "4.1.3", download_bootstrap)

        # jquery
        def download_jquery(version):
            dest = os.path.join(theme_path,"resources","jquery.min.js")
            print("Installing 'jQuery' to '"+dest+"'")
            downloadFileTo("https://code.jquery.com/jquery-"+version+".min.js",dest)
        version_file = os.path.join(theme_path,"version_jquery")
        getOrCreateVersionFile(version_file, "3.3.1", download_jquery)

        # popper
        def download_popper(version):
            dest = os.path.join(theme_path,"resources","popper.min.js")
            print("Installing 'Popper' to '"+dest+"'")
            downloadFileTo("https://unpkg.com/popper.js/dist/umd/popper.min.js",dest)
        version_file = os.path.join(theme_path,"version_popper")
        getOrCreateVersionFile(version_file, "current", download_popper)

        # highlight
        def download_highlight(version):
            # js
            dest = os.path.join(theme_path,"resources","highlight.min.js")
            print("Installing 'highlight' to '"+dest+"'")
            downloadFileTo("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/"+version+"/highlight.min.js",dest)
            # css
            dest = os.path.join(theme_path,"resources","highlight_default.min.css")
            print("Installing 'highlight' to '"+dest+"'")
            downloadFileTo("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/"+version+"/styles/default.min.css",dest)
        version_file = os.path.join(theme_path,"version_highlight")
        getOrCreateVersionFile(version_file, "9.14.2", download_highlight)

        # mathjax
        def download_mathjax(version):
            dest = os.path.join(theme_path,"resources","MathJax")
            print("Installing 'mathjax' to '"+dest+"'")
            downloadZipTo("https://github.com/mathjax/MathJax/archive/"+version+".zip", dest)
        version_file = os.path.join(theme_path,"version_mathjax")
        getOrCreateVersionFile(version_file, "2.7.5", download_mathjax)

        # theme resources
        pkgfileTo(("luke.themes.html.documentation","resources/docs.css"),os.path.join(theme_path,"resources","docs.css"))

        def download_openiconic(version):
            dest = os.path.join(theme_path,"resources","openiconic")
            print("Installing 'openiconic' to '"+dest+"'")
            downloadZipTo("https://github.com/iconic/open-iconic/archive/master.zip", dest)
        version_file = os.path.join(theme_path,"version_openiconic")
        getOrCreateVersionFile(version_file, "current", download_openiconic)





