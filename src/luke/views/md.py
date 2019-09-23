import sys
import hashlib
import re
import os

try:
    from StringIO import StringIO as IOBuffer
except ImportError:
    from io import StringIO as IOBuffer

from luke.views.View import apply_scope
from luke.views.View import View
from luke.parser.markdown import MLList

default_theme = "default"

class md(View):
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
        if hlevel == 1:
            return "\n" + title + "\n" + "="*len(title) + "\n" + content
        if hlevel == 2:
            return "\n" + title + "\n" + "-"*len(title) + "\n" + content
        return "\n\n"+"#"*hlevel+" " + title + "\n" + content

    @apply_scope()
    def translate_hardbreak(self, var, run):
        return "\n\n"

    @apply_scope()
    def translate_olist(self, var, run):
        list_content = var("content")
        ret = ""
        for li in list_content:
            if isinstance(li, dict) and li["type"] in ["ulist", "olist"]:
                ret += " 1. "+run(li)+"\n"
            else:
                ret += " 1. "+ run(li,add_scope={"internal": {"listmode": True}}) +"\n"
        return ret

    @apply_scope()
    def translate_ulist(self, var, run):
        list_content = var("content")
        ret = ""
        for li in list_content:
            if isinstance(li, dict) and li["type"] in ["ulist", "olist"]:
                ret += " * "+run(li)+"\n"
            else:
                ret += " * "+ run(li,add_scope={"internal": {"listmode": True}}) +"\n"
        return ret

    @apply_scope(insertBy="ref", insertFrom="link")
    def translate_link(self, var, run):
        href = var('dest')
        content = run(var(['content', 'dest'], ""), add_scope={"internal": {"paragraphmode": True}})
        return "["+content+"]("+href+")"

    @apply_scope()
    def translate_code_block(self, var, run):
        verbatim = View.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var)
        return "```"+var(['syntax', 'code-syntax'], 'nohighlight')+"\n"+verbatim+"\n```"

    @apply_scope()
    def translate_emph(self, var, run):
        return "*"+run(var('text'))+"*"

    @apply_scope()
    def translate_strong(self, var, run):
        return "**"+run(var('text'))+"**"

    @apply_scope()
    def translate_bold(self, var, run):
        return "__"+run(var('text'))+"__"

    @apply_scope()
    def translate_italic(self, var, run):
        return "_"+run(var('text'))+"_"

    @apply_scope()
    def translate_strike(self, var, run):
        return "~~"+run(var('text'))+"~~"

    @apply_scope(insertBy="ref", insertFrom="image")
    def translate_image(self, var, run):
        href = var('dest')
        content = run(var(['content', 'dest'], ""), add_scope={"internal": {"paragraphmode": True}})
        alt = run(var('alt_text', "")).strip()
        return "!["+content+"]("+href+" \""+alt+"\")"

    @apply_scope()
    def translate_table(self, var, run):
        alignment = {
            'centered': "text-center",
            'center': "text-center",
            'normal': "text-left",
            'left': "text-left",
            'right': "text-right"
        }
        table_content = var('content')
        header = table_content[0]
        coltyp = table_content[1]
        cols = len(header)

        tablestr = ""

        for idx in range(cols):
            tablestr += "| "+run(header[idx]).strip()+" "
        tablestr += "|\n"

        for idx in range(cols):
            tablestr += "| "+"---"+" "
        tablestr += "|\n"

        for row in table_content[2:]:
            for idx in range(cols):
                tablestr += "| "+run(row[idx])+" "
            tablestr += "|\n"

        return tablestr

    @apply_scope()
    def translate_code_inline(self, var, run):
        verbatim = View.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var)
        return "`"+verbatim+"\n`"

    @apply_scope()
    def translate_quote(self, var, run):
        return "> "+var("content")

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def translate_footnote(self, var, run):
        text = run(var('text'), add_scope={"internal": {"paragraphmode": True}}).strip()
        ref = var('ref','')
        return "["+ref+"]^["+text+"]"

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def translate_note(self, var, run):
        text = run(var('text'), add_scope={"internal": {"paragraphmode": True}}).strip()
        ref = var('ref','')
        return "["+ref+"]^["+text+"]"

    @apply_scope()
    def translate_paragraph(self, var, run):
        return run(var("content"))

    @apply_scope()
    def translate_indent(self, var, run):
        return "\t"+run(var('content'))

    @apply_scope()
    def translate_url(self, var, run):
        return var("dest")

    @apply_scope()
    def translate_hrule(self, var, run):
        return "\n---\n"

    @apply_scope()
    def translate_softbreak(self, var, run):
        return "\n"


    # ====================== #
    # preconfigured commands #
    # ====================== #

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



    def __init__(self, theme_name="md"):
        super().__init__()
        self.filesuffix = ".out.md"
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
        treevar = lambda var,alt: tree["scope"]["variable"][var] if "scope" in tree and "variable" in tree["scope"] and var in tree["scope"]["variable"] else alt

        path_file = treevar("absolute_path","./file.md")
        if settings["out_here"]:
            path_out = cwd
        else:
            path_out = os.path.dirname(path_file)
        outfilename = os.path.join(path_out,os.path.basename(os.path.splitext(path_file)[0]) + "_out.md")

        if settings["verbose"] >= 1:
            print("Saving to: "+outfilename)
        with open(outfilename, "wb") as outfile:
            outfile.write(content.encode('utf-8').strip())




View = md
