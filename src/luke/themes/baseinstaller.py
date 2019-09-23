from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import os
import errno
import urllib
import shutil
import pkgutil

def downloadZipTo(srcurl,target,verbose=False,skipBaseFolder=1):
    url = urlopen(srcurl)
    with ZipFile(BytesIO(url.read())) as my_zip_file:
        for contained_file in my_zip_file.namelist():
            target_file = "/".join(contained_file.split("/")[skipBaseFolder:])
            target_path = os.path.join(target, target_file)
            if verbose:
                print(contained_file, " -> ", target_file)

            # create directory if not existant
            if not os.path.exists(os.path.dirname(target_path)):
                try:
                    os.makedirs(os.path.dirname(target_path))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise

            # stop if file to write is a directory
            if os.path.isdir(target_path):
                continue

            # write content of zip-file
            with open(target_path, "wb") as output:
                output.write(my_zip_file.open(contained_file).read())
            # for line in my_zip_file.open(contained_file).readlines():
            #     print(line)
                # output.write(line)

def downloadFileTo(srcurl,dest):
    with urllib.request.urlopen(srcurl) as srcfile:
        with open(dest,"w") as destfile:
            destfile.write(srcfile.read().decode("utf8"))


def getOrCreateVersionFile(version_file, version, downloadfn):
    # download bootstrap
    download = True
    if os.path.exists(version_file):
        with open(version_file) as f:
            version_file_content = f.readline()

        if version  == version_file_content:
            download = False

    if download:
        downloadfn(version)

    # remember version for next query
    with open(version_file, "w") as f:
        f.write(version )


def pkgfileTo(srcpath,dest):
    data = pkgutil.get_data(srcpath[0], srcpath[1])
    with open(dest, 'wb') as fp:
        fp.write(data)


class BaseInstaller():
    def install(theme_path,theme_name="vctheme"):
        theme_path = os.path.join(theme_path,theme_name,"resources")
        # shutil.copytree(theme_path, path_resources_dest)
