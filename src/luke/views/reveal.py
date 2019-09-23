import sys
import hashlib
import re

try:
    from StringIO import StringIO as IOBuffer
except ImportError:
    from io import StringIO as IOBuffer

from luke.views.View import apply_scope
from luke.views.View import View
from luke.views.html import html
from luke.parser.markdown import MLList

default_theme = "reveal"

class reveal(html):
    """
    A class which htmlifies a given tree structure.
    """

    def __init__(self,*args,**settings):
        super().__init__()
        super().__init__(*args,**settings)

        self.filesuffix = ".html"
        self.defaulttheme = "reveal"

        # add extra styles
        self.translate_styles.update({
            "section": {"section": True},
            "notes": {"notes": True},
            "fragment": {"fragment": True},
            "pos": {"pos": True},
            "align": {"align": True}
        })

        self.section_level = 0

    @apply_scope()
    def translate_code_block(self, var, run):
        syntax = var(['syntax', 'code-syntax'], 'nohighlight')
        verbatim = View.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var)
        if syntax == "inject":
            return var('verbatim')

        whitespace = var('whitespace', '')
        if not var('notrim', False) and whitespace != '':
            verbatim = re.sub("^"+whitespace, "", verbatim)
            verbatim = re.sub("\n"+whitespace, "\n", verbatim)
        verbatim.replace("<","&lt;")
        verbatim.replace(">","&gt;")

        return html.make_main_tag(var, "code", tag_class="{1}", tag_style="margin:0", content="""<pre>{0}</pre>""") \
                .format(verbatim, syntax)

    @apply_scope(getVars=True)
    def translate_section_section(self, x, scopes, var, run):
        level = var('h-level')+1
        closing = ""

        # go level down
        if level > self.section_level:
            self.section_level = level
            if self.section_level > 2:
                raise ValueError("maximal Section-Level (2) reached")
        else:
            closing += "\n"+"\t"*(self.section_level)+"</section>\n"*(self.section_level+1-level)
            self.section_level = level

        del x["section"]
        if var("title")[0][0] == ".":
            x = x["content"]

        return closing+"<section>\n"+"\t"*level+run(x)

    @apply_scope()
    def translate_notes_section(self, var, run):
        return "<aside class=\"notes\">\n"+"\t"+run(var("content"))+"</aside>"

    @apply_scope(getVars=True)
    def translate_any_pos(self, x, scope, var, run):
        del x["pos"]
        left = str(var("left","0"))
        top = str(var("top","0"))
        return "<span style=\"position: absolute; top:"+top+"px; left:"+left+"px;\">{}</span>".format(run(x))

    @apply_scope(getVars=True)
    def translate_any_fragment(self, x, scope, var, run):
        del x["fragment"]
        fragment_type = var("fragment-type","")
        fragment_id = var(["fragment-id","fragment-index"],"")
        if fragment_id:
            fragment_id = "data-fragment-index=\""+str(fragment_id)+"\""
        return "<span class=\"fragment "+fragment_type+"\" "+fragment_id+">{}</span>".format(run(x))

    @apply_scope(getVars=True)
    def translate_any_align(self, x, scope, var, run):
        alignment = {
            'centered': "center",
            'center': "center",
            'normal': "left",
            'left': "left",
            'right': "right"
        }
        del x["align"]
        align = var("align-dir","center");
        if align != "center":
            return "<div style=\"text-align:"+alignment[align]+"\">"+str(run(x))+"</div>"
        return run(x)
        return "<span class=\"fragment\">{}</span>".format(run(x))


    @apply_scope(getVars=["cols"])
    def cmd_leftright(self, var, run, cols=2):
        arguments = var("arguments")
        content = ""
        for i in range(cols):
            content += """<div style="width:50%; display:block; float:left;">"""+run(arguments[i])+"</div>"
        return content






    @apply_scope()
    def translate_image(self, var, run):
        alt = run(var('alt_text', "")).strip()
        title = run(var('content', ""))
        width = var('width', "")
        if width:
            width = "width:"+str(width)+"%;"
        src = var('dest')

        return html.make_main_tag(var, "figure", tag_style="display: block; margin: 0;", tag_class=["figure","text-center"], content="""
              <img src="{src}" class="" alt='{alt}' style="{width}">
              <figcaption class="figure-caption">{title}</figcaption>
        """).format(src=src, alt=alt, title=title, width=width)



    @apply_scope()
    def translate_paragraph(self, var, run):
        return str(run(var('content')))

View = reveal
