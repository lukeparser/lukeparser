import sys
import json
from pathlib import Path
from datetime import datetime
import re
import tempfile
import os
import subprocess
import shutil
import queue
import threading
import urllib.request
import hashlib
from tempfile import gettempdir
from luke.defaults import defaults
from luke.parser.markdown import MLList
from luke import __version__

class notfound:
    pass

# decorate a translator-functon to
#   - execute the run-command by adding the current scope to the scopelist
#   - get variables by name (use nearest scope first)
def apply_scope(insertBy=None, insertFrom=None, getVars=False):
    def apply_scope(translate_x):
        def translate_x_with_scope(self, x, scopes):

            # get variable by name (consider parent scopes)
            def var(name, alt=None, scopes=scopes, scope="variable", ignore_scopes=0, ignore_self=False, get_self=False, only_self=False):
                if get_self:
                    return x

                # if multiple variables given, try all out until one is found
                if isinstance(name, list):
                    for n in name:
                        res = var(n, "", scopes=scopes, scope=scope)
                        if res != "":
                            return res
                    if alt is None:
                        raise ValueError("Variable " + " or ".join(name) + " not found in Object of type " + x["type"])
                    else:
                        return alt

                # try to find the right variable in the scopes
                if name in x and not ignore_self:
                    return x[name] if not (isinstance(x[name],dict) and "type" in x[name] and x[name]["type"] == "placeholder") else self.translate_command(x[name], scopes) # else: is placeholder itself!

                # first check the scope insertFrom[x[insertBy]]
                for i,s in enumerate(scopes[len(scopes)-1-ignore_scopes::-1]):
                    i_real = len(scopes)-1-ignore_scopes - i

                    if insertBy is not None and insertFrom is not None:
                        if insertFrom in s and insertBy in x and x[insertBy] in s[insertFrom] and name in s[insertFrom][x[insertBy]]:
                            return s[insertFrom][x[insertBy]][name] if not isinstance(s[insertFrom][x[insertBy]][name],dict) else self.translate_command(s[insertFrom][x[insertBy]][name], scopes[i_real:])

                for i,s in enumerate(scopes[len(scopes)-1-ignore_scopes::-1]):
                    i_real = len(scopes)-1-ignore_scopes - i

                    if scope in s and name in s[scope]:
                        return s[scope][name] if not (isinstance(s[scope][name],dict) and "type" in s[scope][name] and s[scope][name]["type"] == "placeholder") else self.translate_command(s[scope][name], scopes[i_real:])

                if alt is None:
                    raise ValueError("Variable " + name + " not found in Object of type " + x["type"])
                else:
                    return alt

            # evaluate sub-variables, while adding the current scope (if existant)
            def run(x_sub, scopes=scopes, add_scope=None):
                if "scope" in x and x["scope"] != {}:
                    scopes = scopes + [x["scope"]]
                if add_scope is not None:
                    scopes = scopes + [add_scope]
                scopes = scopes[:]
                # scopes = scopes + [{"internal": {"callee": x_sub}}]

                return self.runWithScope(x_sub, scopes)

            if getVars == True:
                return translate_x(self, x, scopes, var, run)
            elif isinstance(getVars,list):
                args = {}
                nargs = x["nargs"] if "nargs" in x else [] #nameless args
                if len(nargs) > 0:
                    nargs = [var(n["command"]) if isinstance(n,dict) and "type" in n and n["type"] == "placeholder" else n for n in nargs]
                nargs_offset = 0

                for k in range(len(getVars)):
                    varname = getVars[k]

                    # first, fill with nargs
                    if k-nargs_offset < len(nargs):
                        if varname == "scopes":
                            args[varname] = scopes
                            nargs_offset += 1
                        elif varname == "adict":
                            args[varname] = x
                            nargs_offset += 1
                        else:
                            args[varname] = nargs[k-nargs_offset]

                    # now, look for default parameters or string-parameters
                    else:
                        if varname == "scopes":
                            args[varname] = scopes
                        elif varname == "adict":
                            args[varname] = x
                        elif varname in x:
                            args[varname] = x[varname]

                return translate_x(self, var, run, **args)
            return translate_x(self, var, run)

        return translate_x_with_scope

    return apply_scope


class View():
    def __init__(self, **settings):
        self.defaults = {**defaults, **settings}

        self.defaulttheme = "raw"
        self.ref = {}
        self.imgref = {}
        self.numbering = 0
        self.indent = 0
        self.filesuffix = None
        self.mathinline_template = "\\({}\\)"
        self.mathblock_template = "\\[{}\\]"

        self.typelator = {
            'MLList': self.handle_mllist,
            'list': self.handle_list,
            'dict': self.handle_dict,
            'str': self.handle_str,
            'bool': self.handle_str,
            'float': self.handle_str,
            'int': self.handle_str
        }

        self.translator = {
            'document': self.translate_document,
            'error': self.translate_error,
            'attributes': self.translate_attributes,
            'math_inline': self.translate_math_inline,
            'math_block': self.translate_math_block,
            'latex_command': self.translate_latex_command,
            'command': self.translate_command,
            'placeholder': self.translate_command,
            'tikz': self.translate_tikz,
        }

        self.translate_styles = {}
        self.tikz_counter = 0

        self.thread_queue = queue.Queue()
        self.thread_num = 0
        self.thread_later_start = {}

    def replace_in_verbatim(self, verbatim, replaceObj, var, run):
        for replace, to in replaceObj.items():
            if replace=="nargs":
                continue
            if isinstance(to, dict) and not ("type" in to and to["type"] == "placeholder"):
                verbatim = verbatim.replace(replace, var(to["name"], to["name"]))
            else:
                verbatim = verbatim.replace(replace, run(to,add_scope={"internal":{"paragraphmode":True}}))
        return verbatim

    def rawtext(text):
        s = ""
        if isinstance(text, dict):
            if "content" in text:
                s += " ".join([View.rawtext(c) for c in text["content"]])
            if "text" in text:
                s += " ".join([View.rawtext(c) for c in text["text"]])
        elif isinstance(text, list):
            s += " ".join([View.rawtext(c) for c in text])
        else:
            s = str(text)
        return s

    @apply_scope()
    def translate_document(self, var, run):
        return run(var('content'))

    @apply_scope()
    def translate_error(self, var, run):
        raise var("exception-object")
        return ""

    @apply_scope(getVars=True)
    def translate_attributes(self, attr, scopes, var, run):
        attr.pop("type", None)
        def walk(attr):
            for k,val in attr.items():
                if isinstance(val,dict):
                    if len(val.keys()) == 1 and "nargs" in attr:
                        attr[k] = run(val["nargs"])
                    elif "type" in val and val["type"] == "placeholder":
                        attr[k] = run(val)
                    else:
                        walk(val)
        walk(attr)

        scope_id = -2 if var("paragraphmode",False,scope="internal",scopes=scopes[-1:]) else -1
        if "variable" not in scopes[scope_id]:
            scopes[scope_id]["variable"] = attr
        else:
            scopes[scope_id]["variable"].update(attr)
        return ""

    @apply_scope()
    def translate_math_inline(self, var, run):
        ret = ""
        for item in var("verbatim"):
            if isinstance(item, str):
                ret += item
            else:
                ret += run(item, add_scope={"internal": {"mathmode": True}})
        return self.mathinline_template.format(ret)

    @apply_scope(getVars=["adict","scopes"])
    def translate_math_block(self, var, run, adict, scopes):
        ret = ""

        if var("customsyntax",False):
            return self.translate_code_block_customsyntax(adict,scopes)

        id = var("id","")
        if id:
            id = "\\label{"+id+"}"
        tag = var("eqnum","" if not id else True)
        if tag:
            if tag == True:
                counter = var('equation',scope='counter')
                counter[-1]+=1;
                tag = "\\tag{"+str(counter[-1])+"}"
            else:
                tag = "\\tag{"+tag+"}"

        for item in var("verbatim"):
            if isinstance(item, str):
                ret += item
            else:
                ret += run(item, add_scope={"internal": {"mathmode": True}})

        return self.mathblock_template.format(ret+id+tag)

    def handle_str(self, s, scopes):
        return "{}".format(s)

    # type handling
    def handle_mllist(self, alist, scopes, add=""):
        return self.handle_list(alist,scopes,add=" ")

    # type handling
    def handle_list(self, alist, scopes, add=""):
        strret = ""
        last_hardbreak = False
        for i, item in enumerate(alist):

            # no softbreak after hard break
            if isinstance(item, dict) and item["type"] == "hard break":
                strret += self.runWithScope(item, scopes)

            # no softbreak before hard break
            elif len(alist) > i + 1 and isinstance(alist[i + 1], dict) and alist[i + 1]["type"] == "hard break":
                strret += self.runWithScope(item, scopes)

            # no softbreak at the end of a block
            elif len(alist) - 1 == i:
                strret += self.runWithScope(item, scopes)

            # softbreak else
            else:
                strret += self.runWithScope(item, scopes) + add
        return strret

    def handle_dict(self, adict, scopes):

        try:
            mytype = None
            if "type" in adict:
                mytype = adict['type']
            if not mytype:
                raise NotImplementedError("Not implemented type ({})".format(mytype))

            # check if type is valid
            if mytype not in self.translator:
                raise ValueError("Type '"+mytype+"' not defined.")

            # check if fiter matches for other style
            for stylename,style_filter in self.translate_styles.items():
                mytype_styled = "translate_"+stylename+"_"+mytype
                if style_filter.items() <= adict.items() and hasattr(self,mytype_styled) and callable(getattr(self,mytype_styled)):
                    return "{}".format(getattr(self, mytype_styled)(adict, scopes))

                # fall back style
                mytype_styled = "translate_any_"+stylename
                if style_filter.items() <= adict.items() and hasattr(self,mytype_styled) and callable(getattr(self,mytype_styled)):
                    return "{}".format(getattr(self, mytype_styled)(adict, scopes))

            # use default style
            return "{}".format(self.translator[mytype](adict, scopes))
        except Exception as err:
            return "{}".format(self.translator["error"]({"type":"exception","exception-type":"View Exception","exception-object":err}, scopes))

    @apply_scope(getVars=True)
    def translate_command(self, x, scopes, var, run):

        # get command from scope
        skip_scopes = 1 if var("paragraphmode", False, scope="internal") else 0
        name = x["command"].split(".")
        cmd = var(name[0], notfound(), ignore_self=True)

        if not isinstance(cmd,notfound):
            for n in name[1:]:
                cmd = cmd[n]

        elif len(name)>1:
            raise ValueError("Command '"+x["command"]+"' not found.")

        else: # cmd not found
            # else get predefined function
            fn = getattr(self, "cmd_" + x["command"], None)
            if callable(fn):
                return "{}".format(fn(x, scopes))

            # else get translator
            fn = getattr(self, "translate_" + x["command"], None)
            if callable(fn):
                x["content"] = x["arguments"][0]
                x["text"] = x["arguments"][0]
                return "{}".format(fn(x, scopes))

            # else command not found
            raise ValueError("Command '"+x["command"]+"' not found.")

        # is actually function
        if hasattr(cmd,'__call__'):
            try:
                return cmd(self,x,scopes)
            except Exception as err:
                return ""

        # is a dict
        elif isinstance(cmd,dict) and "type" not in cmd:
            import json
            return run(json.dumps(cmd, indent=4))

        # just a value
        return run(cmd,add_scope={"variable":x})

    @apply_scope(getVars=True)
    def cmd_newcommand(self, x, scopes, outer_var, outer_run):
        name = x["nargs"][0]
        nargs = x["nargs"][1:]
        var_scope = dict.copy(x)
        del var_scope["nargs"]
        del var_scope["type"]
        del var_scope["command"]
        del var_scope["arguments"]

        # content of new command
        content = x["arguments"][0]

        # check if is verbatim-command
        scopename = "variable"
        if len(content) == 1 and isinstance(content[0],dict) and content[0]["type"] == "paragraph" and "content" in content[0] and len(content[0]["content"])==1 and isinstance(content[0]["content"][0][0],dict) and "verbatim" in content[0]["content"][0][0]:
            adict = content[0]["content"][0][0]
            if adict["type"] == "math_block" or adict["type"] == "math_inline":
                adict["mathmode"] = True
                var_scope["automath"] = adict["type"]
            content = content[0]["content"][0][0]["verbatim"]
        var_scope["content"] = content

        # getVars nargs for exception handling
        @apply_scope(getVars=["adict"]+nargs)
        def cmd(self, var, run, adict, **nargs):
            inner_scope = dict.copy(var_scope)
            content = var_scope["content"]
            inner_scope.update(adict)
            if "command" in inner_scope:
                del inner_scope["command"]
            if "type" in inner_scope:
                del inner_scope["type"]
            if "nargs" in inner_scope:
                del inner_scope["nargs"]
            if "arguments" in inner_scope:
                del inner_scope["arguments"]
            inner_scope.update(nargs)
            arguments = var("arguments",[])
            for i,arg in enumerate(arguments):
                inner_scope["arg"+str(i)] = arg
            math = var("automath",var_scope["automath"] if "automath" in var_scope else False)
            if math and not var("mathmode", False, scope="internal"):
                content = {'type': math, 'verbatim': content}
            return run(content,add_scope={"variable":inner_scope})

        scope_id = -2 if outer_var("paragraphmode",False,scope="internal",scopes=scopes[-1:]) else -1
        if scopename not in scopes[scope_id]:
            scopes[scope_id][scopename] = {name:cmd}
        else:
            scopes[scope_id][scopename][name] = cmd

        return ""

    # @apply_scope(insertBy="command", insertFrom="latex_command")
    @apply_scope(getVars=True)
    def translate_latex_command(self, x, scopes, var, run):
        # get command from scope
        skip_scopes = 1 if var("paragraphmode", False, scope="internal") else 0
        name = x["command"].split(".")
        cmd = var(name[0], False, ignore_self=True)

        if cmd:
            for n in name[1:]:
                cmd = cmd[n]

        elif len(name)>1:
            raise ValueError("Command '"+x["command"]+"' not found.")

        else:
            # else get predefined function
            fn = getattr(self, "cmd_" + x["command"], None)
            if callable(fn):
                return "{}".format(fn(x, scopes))

            # else get translator
            fn = getattr(self, "translate_" + x["command"], None)
            if callable(fn):
                x["content"] = x["arguments"][0]
                x["text"] = x["arguments"][0]
                return "{}".format(fn(x, scopes))

            # else command not found (pass to latex)
            arguments = var('arguments', [])
            if len(arguments) > 0:
                args = "{" + "}{".join(["".join(run(si) for si in s) for s in arguments]) + "}"
                return "\\{command}{args}".format(command=var('command'), args=args)
            return "\\{command}".format(command=var('command'))

        # is actually function
        if hasattr(cmd,'__call__'):
            try:
                return cmd(self,x,scopes)
            except Exception as err:
                return ""

        # is a dict
        elif isinstance(cmd,dict) and "type" not in cmd:
            import json
            return run(json.dumps(cmd, indent=4))

        # just a value
        return run(cmd)

    @apply_scope(getVars=["scopes","name"])
    def cmd_component(self, var, run, scopes, name):
        components = scopes[0]["components"]
        if name not in components:
            components[name] = ""
        arguments = var("arguments")
        components[name] += run(arguments[0],add_scope={"internal":{"paragraphmode":True}})
        return ""

    @apply_scope(getVars=True)
    def translate_tikz(self, x, scopes, var, run):
        code = x.pop('tikz-code')
        usetikzlibrary = var('usetikzlibrary',"")
        additional_code = var('additional_code',"")
        if usetikzlibrary.strip():
            usetikzlibrary = "\\usetikzlibrary{"+usetikzlibrary+"}"
        x.pop('type')
        latexpackages = var('latexpackages',"")
        latexpackages = "\n".join(["\\usepackage{"+package+"}" for package in latexpackages.split(",")])
        svgfile = os.path.join(var("assets"),var("filename")+"_"+str(self.tikz_counter)+".svg")
        self.tikz_counter += 1
        syspath = lambda file : os.path.join(var("basepath"),file)
        code_hashed = "<!-- "+hashlib.sha256(code.encode()).hexdigest()+" -->"

        if os.path.exists(syspath(svgfile)):
            with open(syspath(svgfile)) as svg:
                svg.readline() # skip first line
                svg_matches = code_hashed == svg.readline()[:-1]
        else:
            svg_matches = False

        if not svg_matches:
            temp_dir = tempfile.mkdtemp()

            texfile_path = os.path.join(temp_dir,"tikz.tex")
            with open(texfile_path, "w") as texfile:
                texfile.write("""
                \\documentclass[crop,tikz,convert={outext=.svg,command=\\unexpanded{pdf2svg \\infile\\space\\outfile}},multi=false]{standalone}[2012/04/13]
                \\usepackage{pgfplots}
                """+usetikzlibrary+"""
                """+latexpackages+"""
                """+additional_code+"""
                \\makeatother
                \\begin{document}
                \\begin{tikzpicture}"""+code+"""
                \\end{tikzpicture}
                \\end{document}
                """)

            try:
                origdir = os.getcwd()
                os.chdir(temp_dir)
                output = subprocess.check_output(
                    ['pdflatex','-interaction=nonstopmode', texfile_path], stderr=subprocess.STDOUT,  universal_newlines=True)

                pdffile_path = os.path.join(temp_dir,"tikz.pdf")
                svgfile_path = os.path.join(temp_dir,"tikz.svg")
                subprocess.call(['pdf2svg', pdffile_path, svgfile_path])

            except subprocess.CalledProcessError as exc:
                # strip all lines until first error
                output = []
                found = False
                for line in exc.output.split("\n"):
                    if line.startswith("!"):
                        found = True
                    if found:
                        output.append(line)
                output = exc.output if not found else "\n".join(output)

                return run({"type":"error","exception-type":"View Exception","exception-object":output+"\nthis results in the exit return code: "+str(exc.returncode)}, scopes)
            finally:
                os.chdir(origdir)


            # shutil.move(svgfile_path, os.path.join(var("basepath"),svgfile))
            with open(svgfile_path,"r") as tmpsvg:
                with open(syspath(svgfile), "w") as destsvg:
                    once = True
                    for line in tmpsvg:
                        destsvg.write(line)
                        if once:
                            destsvg.write(code_hashed+"\n")
                            once = False
        return run({'type': 'image', 'dest': svgfile, **x})



    @apply_scope(getVars=["format"])
    def cmd_lastchange(self, var, run, format="%d. %B %Y, %H:%M:%S"):
        absolute_path = var("absolute_path")
        timestamp = datetime.fromtimestamp(Path(absolute_path).stat().st_mtime)
        return ("{:"+format+"}").format(timestamp)

    @apply_scope(getVars=["format"])
    def cmd_date(self, var, run, format="%d. %B %Y"):
        return ("{:"+format+"}").format(datetime.now())

    @apply_scope(getVars=["scopes","file","inplace","hidden"])
    def cmd_include(self, var, run, scopes, file, inplace=True, hidden=False):
        from luke.luke import parse_lang
        from luke.parser.markdown import Parser
        from luke.Preprocessing import Preprocessing

        basepath = var("basepath")
        file = os.path.join(basepath,file)
        if file.endswith(".md") or file.endswith(".json"):
            snd = parse_lang(Parser(), Preprocessing(), file)
            if hidden:
                run(snd)
                return ""
            if inplace:
                return run(snd["content"])
            return run(snd)
        else:
            with open(file,"r") as f:
                content = f.read() #.decode("utf8")
                return content

            # return res

    @apply_scope(getVars=["filter","sub"])
    def cmd_listdocuments(self,var,run,filter="[0-9]+-?(.*)((.md)|/)",sub="\\1"):
        basepath = run(var("basepath"))
        basepath = os.path.realpath(basepath)+os.sep
        currentpath = var("basepath",ignore_self=True)
        currentpath_real = os.path.realpath(currentpath)
        currentfile_real = var("absolute_path")
        if os.sep == "\\":
            filter = filter.replace("/",os.sep+os.sep)
            
        def dir2content(basepath,rootdir):
            files = [f+os.sep if os.path.isdir(os.path.join(basepath,f)) else f for f in os.listdir(basepath)]
            files = sorted(files)
            files = [(re.sub(filter,sub,f).replace("-"," "),f) for f in files if re.match(filter,f) and not f.startswith("index\\.")]
            relpath = os.path.relpath(basepath,rootdir)
            content = {
                "type":"ulist","list-symbol":"none","content":
                    [
                        [[{"type":"link","dest": os.path.join(relpath,f), "content": {"type": "strong","text":name} if os.path.join(basepath,f) == currentfile_real else name}]] if not os.path.isdir(os.path.join(basepath,f)) or currentpath_real not in os.path.join(basepath,f) else
                        [[{"type":"link","dest": os.path.join(relpath,f), "content": name if os.path.join(relpath,f) in currentpath_real else {"type": "strong","text":name}}], dir2content(os.path.join(basepath,f),rootdir)]
                        for name,f in files
                    ]
            }
            return content

        content = dir2content(basepath,currentpath)

        return run(content)


    @apply_scope(getVars=["scopes","id","tempfile"])
    def cmd_arxiv(self, var, run, scopes, id, tempfile=True):

        def deferred_arxiv(q,i,id):

            strid = str(id)
            tmpdir = gettempdir()
            idfile = os.path.join(tmpdir,"luke_arxiv_"+strid.replace("/","_"))
            if tempfile and os.path.exists(idfile):
                with open(idfile, "r") as textfile:
                    xmltext = textfile.read() #.decode("utf8")

            else:
                with urllib.request.urlopen("https://arxiv.org/api/query?id_list="+strid) as fp:
                    mybytes = fp.read()
                    xmltext = mybytes.decode("utf8")
                    if tempfile:
                        with open(idfile,"w") as textfile:
                            textfile.write(xmltext)

            titleRE = re.compile("<title>([^<]+?)</title>")
            title_groups = titleRE.search(xmltext)
            title = title_groups.group(1)
            # num = title_groups.group(1)
            num = "["+strid+"]"

            # append
            content = [{"type":"link","dest": "https://arxiv.org/abs/"+strid, "content": num}, " ", title, " ", {"type":"link","dest": "https://arxiv.org/pdf/"+strid+".pdf", "content": {"command": "icon", "nargs": ["document"],"type": "command"}}]

            q.put((i,run(content)))

        tmp_str = "{{thread_"+str(self.thread_num)+"}}"
        t = threading.Thread(target=deferred_arxiv, args = (self.thread_queue,self.thread_num,id))
        t.daemon = True
        t.start()

        self.thread_num += 1
        return tmp_str

    @apply_scope(getVars=["scopes", "l", "r"])
    def cmd_ifeq(self, var, run, scopes, l, r):
        arguments = var("arguments")
        if l==r:
            return run(arguments[0])
        else:
            return run(arguments[1])

    @apply_scope(getVars=["scopes", "l", "r"])
    def cmd_ifneq(self, var, run, scopes, l, r):
        arguments = var("arguments")
        if l!=r:
            return run(arguments[0])
        else:
            return run(arguments[1])

    @apply_scope(getVars=["scopes", "to", "start", "step", "index", "list"])
    def cmd_for(self, var, run, scopes, to=0, start=0, step=1, index="i", list=[]):
        arguments = var("arguments")
        s = ""
        if len(list) == 0:
            for i in range(start,to,step):
                s += run(arguments[0], add_scope={"variable":{index: i}})
        else:
            for i,obj in enumerate(list["nargs"]):
                obj[index] = i
                s += run(arguments[0], add_scope={"variable":obj})
        return s

    @apply_scope()
    def cmd_n(self, var, run):
        return "\n"

    @apply_scope()
    def cmd_block(self, var, run):
        return run(var("arguments")[0])

    @apply_scope()
    def cmd_version(self, var, run):
        return run(__version__)

    def runWithScope(self, tree, scope):
        mytype = str(type(tree).__name__)
        if mytype in self.typelator:
            return self.typelator[mytype](tree, scope)
        else:
            raise TypeError("Can't handle this type! ({})".format(mytype))

    def run(self, tree, **settings):
        classname = self.__class__.__name__
        themename = settings["theme"] if "theme" in settings else "default"

        try:
            theme = __import__("luke.themes."+classname+"."+themename, fromlist=['']).Theme
        except ModuleNotFoundError:
            theme = False
            pass

        # ---------#
        # preparse #
        # ---------#
        if theme:
            tree = theme.preparse(tree)

        # ------------------ #
        # parse content-tree #
        # ------------------ #
        internals = settings["internal_variables"] if "internal_variables" in settings else {}
        global_scope = {"counter":{k:[0] for k in self.counters}, "footnotes": {"buffer":[]}, "internal":{"contentlist":[], **internals}, "components": {}, "variable": {"view": self.__class__.__name__}}
        if "content" in tree:
            tree["content"].append({
                "command": "footnotes",
                "type": "command"
            })
        result = self.runWithScope(tree, [global_scope])
        tree["global_scope"] = global_scope

        # ----------#
        # postparse #
        # ----------#
        if theme:
            global_scope = theme.postparse(global_scope)

        # start deferred threads
        for t_id,t in self.thread_later_start.items():
            t.start()

        # get thread-results
        thread_results = {}
        for ti in range(self.thread_num):
            i, val = self.thread_queue.get()
            thread_results[i] = val

        # replace in target
        for i in range(self.thread_num):
            result = result.replace("{{thread_"+str(i)+"}}", thread_results[i])
            for name,content in global_scope["components"].items():
                global_scope["components"][name] = global_scope["components"][name].replace("{{thread_"+str(i)+"}}", thread_results[i])

        return result


    def listThemes(self):
        return [("[raw.]"+self.__class__.__name__.split(".")[-1],"preinstalled")]


