from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import os
import errno
import urllib
import shutil
import pkgutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor


# =============== #
# download helper #
# =============== #

# download & extract zip file
def extractZipTo(bfile,target,pbar,verbose=False,skipBaseFolder=1):

    # parse zip file
    with ZipFile(BytesIO(bfile)) as my_zip_file:
        pbar.total = len(my_zip_file.namelist())
        pbar.unit = "files"
        for contained_file in my_zip_file.namelist():
            pbar.update(1)
            target_file = os.sep.join(contained_file.split("/")[skipBaseFolder:])
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


# download single file
def saveFileTo(bfile,target,pbar):
    pbar.total = 1
    with open(target,"wb") as destfile:
        destfile.write(bfile)
    pbar.update(1)

# save package file
def pkgfileTo(srcpkg, srcpkg_path,target,pbar):
    pbar.total = 1
    data = pkgutil.get_data(srcpkg, srcpkg_path)
    with open(target, 'wb') as fp:
        fp.write(data)
    pbar.update(1)

# download with progress bar
def download(srcurl, pbar):
    url = urlopen(srcurl)
    total_length = url.info().get("Content-Length")

    # download file with tqdm
    if total_length is not None:
        chunksize = 2**12
        bfile = bytearray()
        pbar.total = int(total_length)
        for i in range(int(total_length)//chunksize+1):
            bfile += url.read(chunksize)
            pbar.update(chunksize)
    else:
        pbar.total = 1
        bfile = url.read()
        pbar.update(1)

    return bfile





# ================ #
# resources helper #
# ================ #

# get path to a version file
def version_file(theme_path,args):
    return os.path.join(theme_path,"version_"+args["name"])

# get path to a version file
def dest(theme_path,args,destfolder=False):
    theme_path = os.path.join(theme_path,"resources")
    if destfolder:
        dest_filename = args["name"]
    else:
        extensions = os.path.basename(args["src"]).split(".")
        extensions = extensions[-2:] if extensions[-2] == "min" else extensions[-1:]
        dest_filename = args["name"]+"."+".".join(extensions)
    return os.path.join(theme_path,dest_filename)

# installs a single resource based on a config object
def install_resource(pbar, theme_path, args):

    # check if is already on system
    if "pkg" in args:
        pbar.set_description(args["name"]+": Installing..")
        pbar.n = 0
        pkgfileTo(args["pkg"],args["src"],dest(theme_path,args),pbar)

    else:
        pbar.set_description(args["name"]+": Downloading..")

        # download the file
        bfile = download(args["src"].format(version=args["version"]),pbar)
        pbar.set_description(args["name"]+": Installing..")
        pbar.n = 0

        # check which downloader to choose
        if args["src"].endswith(".zip") or "type" in args and args["type"] == "zip":
            skipBaseFolder = args["skipBaseFolder"] if "skipBaseFolder" in args else 1
            extractZipTo(bfile,dest(theme_path,args,destfolder=True),pbar,skipBaseFolder=skipBaseFolder)
        else:
            saveFileTo(bfile,dest(theme_path,args),pbar)

        # remember version for download
        with open(version_file(theme_path,args), "w") as f:
            f.write(args["version"])

    pbar.set_description(args["name"]+": Done.")
    pbar.refresh()

# install all resources in parallel
def install_resources(resources, theme_path,theme_name):
    theme_path = os.path.join(theme_path,theme_name)
    resources_path = os.path.join(theme_path,"resources")

    # if theme_path not exists, create directory
    if not os.path.exists(resources_path):
        os.makedirs(resources_path)

    # install all resources
    thread_args, tqdms = [], []
    print("Installing Resources: "+", ".join([key for key,_ in resources.items()]))
    for i, (key, args) in enumerate(resources.items()):
        args["name"] = key
        t = tqdm(desc=key, unit="B", unit_scale=True, leave=False)
        tqdms.append(t)

        # first check for version
        if os.path.exists(version_file(theme_path,args)):
            with open(version_file(theme_path,args)) as f:
                version_file_content = f.readline()

            # skip if version is installed
            if args["version"] == version_file_content:
                t.set_description(key+": Already installed")
                t.total = 1
                t.update(1)
                continue

            # remove if is wrong version
            shutil.rmtree(dest(theme_path,args))
            shutil.rmtree(dest(theme_path,args,destfolder=True))

        thread_args.append((t,theme_path,args))

    with ThreadPoolExecutor() as p:
        p.map(lambda args:install_resource(*args),thread_args)
    # for args in thread_args:
    #     install_resource(*args)

    for t in tqdms:
        t.close()
    print("Installation Complete.")
    

class BaseInstaller():
    def install(theme_path,theme_name="vctheme"):
        theme_path = os.path.join(theme_path,theme_name,"resources")


