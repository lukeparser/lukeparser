import sys
import hashlib
import re
import os
from luke.defaults import defaults
import pkgutil

try:
    from StringIO import StringIO as IOBuffer
except ImportError:
    from io import StringIO as IOBuffer

from luke.views.View import apply_scope
from luke.views.View import View
from luke.parser.markdown import MLList

default_theme = "default"

class latex(View):
    """
    A class which htmlifies a given tree structure.
    """


    # =========== #
    # Translators #
    # =========== #

    @apply_scope()
    def translate_section(self, var, run):
        hlevel = var("h-level",0)+1
        title = run(var("title"))
        content = run(var("content"))
        counter = "" if var('section-counter',True) else "*"
        return "\n\\"+counter+"sub"*(hlevel-1)+"section{" + title + "}\n" + content

    @apply_scope()
    def translate_hardbreak(self, var, run):
        return "\n\n"

    @apply_scope()
    def translate_olist(self, var, run):
        list_content = var("content")
        ret = "\\begin{enumerate}\n"
        for li in list_content:
            if isinstance(li, dict) and li["type"] in ["ulist", "olist"]:
                ret += " \item "+run(li)+"\n"
            else:
                ret += " \item "+ run(li,add_scope={"internal": {"listmode": True}}) +"\n"
        ret = "\n\\end{enumerate}"
        return ret

    @apply_scope()
    def translate_ulist(self, var, run):
        list_content = var("content")
        ret = "\\begin{itemize}\n"
        for li in list_content:
            if isinstance(li, dict) and li["type"] in ["ulist", "olist"]:
                ret += " \item "+run(li)+"\n"
            else:
                ret += " \item "+ run(li,add_scope={"internal": {"listmode": True}}) +"\n"
        ret = "\n\\end{itemize}"
        return ret

    @apply_scope(insertBy="ref", insertFrom="link")
    def translate_link(self, var, run):
        href = var('dest')
        content = run(var(['content', 'dest'], ""), add_scope={"internal": {"paragraphmode": True}})
        return "\\href{"+href+"}{"+content+"}" 

    @apply_scope()
    def translate_code_block(self, var, run):
        verbatim = View.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var)
        return "\\begin{verbatim}\n"+verbatim+"\n\\end{verbatim}"

    @apply_scope()
    def translate_emph(self, var, run):
        return "\\emph{"+run(var('text'))+"}"

    @apply_scope()
    def translate_strong(self, var, run):
        return "\\textbf{"+run(var('text'))+"}"

    @apply_scope()
    def translate_bold(self, var, run):
        return "\\textbf{"+run(var('text'))+"}"

    @apply_scope()
    def translate_italic(self, var, run):
        return "\\textit{"+run(var('text'))+"}"

    @apply_scope()
    def translate_strike(self, var, run):
        return "\\sout{"+run(var('text'))+"}"

    @apply_scope(insertBy="ref", insertFrom="image")
    def translate_image(self, var, run):
        href = var('dest')
        content = run(var(['content', 'dest'], ""), add_scope={"internal": {"paragraphmode": True}})
        alt = run(var('alt_text', "")).strip()
        return "\n\\begin{figure}\n\t\\includegraphics[width=\\linewidth]{"+href+"}\n\t\\caption{"+content+"}\n\t\\label{"+alt+"}\n\\end{figure}"

    @apply_scope()
    def translate_table(self, var, run):
        alignment = {
            'centered': "c",
            'center': "c",
            'normal': "l",
            'left': "l",
            'right': "r"
        }
        table_content = var('content')
        header = table_content[0]
        coltyp = table_content[1]
        cols = len(header)

        tablestr = "\\begin{tabular}{"+" ".join([alignment[c] for c in coltyp])+"}"

        for idx in range(cols):
            tablestr += " & ".join([" \\textbf{"+run(header[idx]).strip()+"}" for idx in range(cols)])
        tablestr += "\\\\\n"

        for row in table_content[2:]:
            for idx in range(cols):
                tablestr += " & ".join([run(row[idx]).strip() for idx in range(cols)])
            tablestr += "\\\\\n"

        return tablestr

    @apply_scope()
    def translate_code_inline(self, var, run):
        verbatim = View.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var)
        return "\\texttt"+verbatim+"}"

    @apply_scope()
    def translate_quote(self, var, run):
        return "”"+var("content")+"“"

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def translate_footnote(self, var, run):
        text = run(var('text'), add_scope={"internal": {"paragraphmode": True}}).strip()
        ref = var('ref','')
        return ref+"\\footnote{"+text+"}"

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def translate_note(self, var, run):
        text = run(var('text'), add_scope={"internal": {"paragraphmode": True}}).strip()
        ref = var('ref','')
        return ref+"\\footnote{"+text+"}"

    @apply_scope()
    def translate_paragraph(self, var, run):
        return run(var("content"))

    @apply_scope()
    def translate_indent(self, var, run):
        return "\t"+run(var('content'))

    @apply_scope()
    def translate_url(self, var, run):
        return "\\url{"+var("dest")+"}"

    @apply_scope()
    def translate_hrule(self, var, run):
        return "\n\\hrule\n"

    @apply_scope()
    def translate_softbreak(self, var, run):
        return "\n"

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def cmd_footnotes(self, var, run):
        footnotes_list = var("buffer",scope="footnotes")
        if len(footnotes_list)==0:
            return ""
        footnote_view_content = [ ["["+str(f["index"])+"] ",MLList(f["content"]), {"type":"new line"}] for f in footnotes_list ]
        footnotes_list.clear()
        footnote_view = [{"type": "hard break"}, {"type": "hrule"}, {"type": "hard break"},
            {
                "content": footnote_view_content,
                "scope": {},
                "type": "paragraph"
            }]
        return run(footnote_view)




    def __init__(self, theme_name="tex"):
        super().__init__(theme_name=theme_name)
        self.filesuffix = ".out.tex"
        self.defaulttheme = "nostyle"
        self.mathinline_template = "${}$"
        self.mathblock_template = "$${}$$"

        self.translator.update({
            'footnote': self.translate_footnote,
            'footnote_inline': self.translate_footnote,
            'note': self.translate_note,
            'note_inline': self.translate_note,
            'olist': self.translate_olist,
            'ulist': self.translate_ulist,
            'section': self.translate_section,
            'hard break': self.translate_hardbreak,
            'table': self.translate_table,
            'image': self.translate_image,
            'link': self.translate_link,
            'emph': self.translate_emph,
            'italic': self.translate_italic,
            'quote': self.translate_quote,
            'strong': self.translate_strong,
            'bold': self.translate_bold,
            'strike': self.translate_strike,
            'hrule': self.translate_hrule,
            'code_inline': self.translate_code_inline,
            'code_block': self.translate_code_block,
            'paragraph': self.translate_paragraph,
            'indent': self.translate_indent,
            'url': self.translate_url,
            'new line': self.translate_softbreak
        })

        # add counters for the following elements
        self.counters = ["section", "equation"]

    def run(self, tree, **settings):
        content = super().run(tree)
        settings = {**defaults, **self.defaults, **settings}

        treevar = lambda var,alt: tree["scope"]["variable"][var] if "scope" in tree and "variable" in tree["scope"] and var in tree["scope"]["variable"] else alt
        classname = self.__class__.__name__

        # ---------------------- #
        # parse in-file settings #
        # ---------------------- #

        # get theme
        theme = settings["theme_name"] if settings["overwrite_theme"] else treevar("theme",settings["theme_name"])
        if theme == "default":
            theme = settings["default_latex_theme"]

        if classname == "reveal":
            reveal_theme = theme
            theme = "reveal"

        # get theme resources
        path_theme = os.path.join(settings["theme_path"],classname,theme)
        path_resources_src = os.path.join(settings["theme_path"],classname,theme,"resources")


        if not settings["to_string"]:

            # ---------------- #
            # parse shorthands # - for file saving
            # ---------------- #
            cwd = os.getcwd()
            path_file = treevar("absolute_path","./file.tex")

            # destination of file (having content)
            if settings["out_here"]:
                path_out = cwd
            else:
                path_out = os.path.dirname(path_file)

            # destination of resources
            if settings["copy_resources"]:
                if settings["resources_here"]:
                    path_resources_dest = os.path.join(cwd,"luke_resources",theme)
                elif settings["resources_with_file"]:
                    path_resources_dest = os.path.join(path_out,"luke_resources",theme)
                else:
                    path_resources_dest = settings["resources_dest"] if settings["resources_dest"] is not None else os.path.join(cwd,"luke_resources",theme)
                path_resources_relative = os.path.relpath(path_resources_dest,path_out)
            else:
                path_resources_dest = None
                if settings["resources_here"]:
                    path_resources_relative = os.path.join(os.path.relpath(cwd,path_out),"luke_resources",theme)
                elif settings["resources_with_file"]:
                    path_resources_relative = os.path.join("luke_resources",theme)
                elif settings["resources_relative"]:
                    path_resources_relative = settings["resources_relative"]
                else:
                    path_resources_relative = path_resources_src

            # outfile settings
            outfilename = os.path.join(path_out,os.path.basename(os.path.splitext(path_file)[0]) + ".tex")

        else:
            path_resources_relative = settings["resources_relative"]


        # ---------------------- #
        # parse in-file settings #
        # ---------------------- #

        # where to find resources when viewing from inside html-document
        resources_relative = treevar("resources_relative",path_resources_relative)

        if settings["resources_relative_append_theme"]:
            resources_relative = os.path.join(resources_relative,theme)




        # ------------------- #
        # get header & footer #
        # ------------------- #

        path_header = os.path.join(path_resources_src,"header.tex")
        path_footer = os.path.join(path_resources_src,"footer.tex")

        # use from copied resource if overwritten
        # else use original file from package
        try:
            if os.path.exists(path_header):
                with open(path_header, "r") as header:
                    header = header.read().format(resources=resources_relative, theme=theme).encode("utf-8")
            else:
                header = pkgutil.get_data("luke.themes."+classname+"."+theme,"header.tex").decode("utf-8")
                header = header.format(resources=resources_relative, theme=theme).encode("utf-8")

            # same with footer-file
            if os.path.exists(path_footer):
                with open(path_footer, "r") as footer:
                    footer = footer.read().format(resources=resources_relative, theme=theme).encode("utf-8")
            else:
                footer = pkgutil.get_data("luke.themes."+classname+"."+theme,"footer.tex").decode("utf-8")
                footer = footer.format(resources=resources_relative, theme=theme).encode("utf-8")
        except:
            raise ValueError("The theme '"+theme+"' does not seem to exist.")

        if settings["to_string"]:
            return header+content.encode("utf-8")+footer

        # ----------------- #
        # write actual file #
        # ----------------- #
        if settings["verbose"] >= 1:
            print("Saving to: "+outfilename)
        with open(outfilename, "wb") as outfile:
            outfile.write(header)
            outfile.write(content.encode('utf-8').strip())
            outfile.write(footer)



View = latex
