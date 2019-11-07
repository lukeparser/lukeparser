import hashlib
import re
import threading
import os
from luke.defaults import defaults
import pkgutil
import luke.themes.html
import shutil
from html import escape
import traceback
import linecache

class format_dict(dict):
    def __missing__(self, key):
        return ""

class str_escaped(str):
    pass

try:
    from StringIO import StringIO as IOBuffer
except ImportError:
    from io import StringIO as IOBuffer

from luke.views.View import apply_scope
from luke.views.View import View
from luke.parser.markdown import MLList

default_theme = defaults["default_html_theme"]

class html(View):
    """
    A class which htmlifies a given tree structure.
    """

    # ----------------
    # Helper Functions
    # ----------------
    def make_main_tag(var, *args, **kwargs):
        return html.make_tag(var, *args, **kwargs, is_main_tag=True)

    def get_classes(var,tag_class=""):
        if not isinstance(tag_class, list):
            tag_class = [tag_class]
        self_x = var("self",get_self=True)
        filter_bool = lambda d: [k for k, v in d.items() if isinstance(v,bool) and v]
        tag_class += filter_bool(self_x)
        return tag_class

    def make_tag(var, tag_name, tag_id="", tag_class="", tag_style="", tag_addition="", content=None, replace_block=True, is_main_tag=False):

        # replace tag, if in paragraphmode
        if tag_name in ["div", "p"] and replace_block and var("paragraphmode", False):
            tag_name = "span"

        # add main-tag related stuff
        if is_main_tag and len(tag_id) == 0:
            tag_id = var("id", "")

        # make attribute-strings
        if tag_id is "":
            pass
        else:
            tag_id = "id=\""+tag_id+"\" "

        tag_class = html.get_classes(var,tag_class)
        if len(tag_class) > 0:
            tag_class = "class=\""+" ".join(tag_class)+"\" "
        else:
            tag_class = ""

        if len(tag_style) == 0:
            if isinstance(tag_style,list):
                tag_style = ""
        elif isinstance(tag_style, list):
            tag_style = "style=\""+";".join(tag_style)+"\" "
        else:
            tag_style = "style=\""+str(tag_style)+"\" "

        if tag_addition is "":
            pass
        elif isinstance(tag_addition, list):
            tag_addition = " ".join(tag_addition)
        else:
            tag_addition = tag_addition

        # make tag
        wrap_start = "<"+tag_name+" "
        wrap_end = ""
        if content is not None:
            wrap_end = content + "</"+tag_name+">"

        return wrap_start+tag_id+tag_class+tag_style+tag_addition+">"+wrap_end



    # =========== #
    # Translators #
    # =========== #

    def handle_str(self, s, scopes):
        if isinstance(s,str_escaped):
            return str(s)
        return escape(str(s))

    @apply_scope()
    def translate_section(self, var, run):
        alignment = {
            'centered': "text-center",
            'center': "text-center",
            'normal': "text-left",
            'left': "text-left",
            'right': "text-right"
        }
        align = alignment[var("align","normal")]

        title = var('title')
        id = View.rawtext(title).strip().replace(" ","-") if var("section-auto-id",True) and not var("id",False) else ""
        title = run(title)
        level = var('h-level')
        counter = var('section',scope='counter')

        if var('alert', False):
            alert = var('alert', False)
            if isinstance(alert,bool):
                alert = 'info'
            return """<div class="alert alert-{alert}" role="alert">
                            <b>{title}</b><hr>
                            {content}
                      </div>""".format(alert=alert, title=title, content=run(var('content')))


        if var('section-counter',False):
            counter[-1]+=1;
            counter_str = ".".join([str(c) for c in counter])+". "
        else:
            counter_str = ""
            counter = []

        # add to contentlist (for later use)
        if var("section-contentlist",True):
            contentlist = var("contentlist",False,scope="internal")
            if isinstance(contentlist,list):
                contentlist.append((counter[:],id,title,level))

        hidden = "hidden" if var('hidden', False) else ""

        # it's a plain section, how boring is that ...
        return "\n".join([
            html.make_main_tag(var, "h{size}", tag_id=id, tag_class="{hidden} "+align, content="{counter}{title}").format(size=(level + 1), title=title, hidden=hidden, counter=counter_str), run(var('content'), add_scope={"counter": {"section": counter+[0]}})
        ])

    @apply_scope()
    def translate_hardbreak(self, var, run):
        if var("listmode", False, scope="internal"):
            return "<br/><br/>"
        return "<br style='display:block; margin:10px 0;'>"

    @apply_scope()
    def translate_olist(self, var, run):
        list_style = var("list-symbol","auto")
        if list_style == "auto":
            symb = var("symbols","1.")[0]
            if symb[0] == "0" and len(symb) >= 3:
                list_style = "decimal-leading-zero"
            elif symb[0] in "ivxlcdm":
                list_style = "lower-roman"
            elif symb[0] in "IVXLCDM":
                list_style = "upper-roman"
            elif symb[0] in "abcdefghijklmnopqrstuvwxyz":
                list_style = "lower-alpha"
            elif symb[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                list_style = "upper-alpha"
            else:
                list_style = "decimal"

        style, classes = [], []
        style.append("list-style-type:"+list_style+";")
        boldlist = var("list-style-bold",False)
        boldlist_s = ""
        boldlist_e = ""
        if boldlist:
            classes.append("list-style-bold")
            boldlist_s = "<span>"
            boldlist_e = "</span>"
        ret = html.make_main_tag(var, "ol", tag_style=style, tag_class=classes)
        list_content = var("content")
        if len(list_content) > 0:
            for li in list_content:
                if isinstance(li, dict) and li["type"] in ["ulist", "olist"]:
                    if li != list_content[0]:
                        ret = ret[:-5]
                    else:
                        ret += "<li>"+boldlist_s
                    ret += run(li)
                    ret += "</li>"+boldlist_e
                else:
                    ret += "<li>"+boldlist_s
                    ret += run(li,add_scope={"internal": {"listmode": True}})
                    ret += "</li>"+boldlist_e
        ret += "</ol>"
        return ret

    @apply_scope()
    def translate_ulist(self, var, run):
        style, classes, attr = [], [], []
        list_style = var("list-symbol","auto-depth")
        listdepth = var("listdepth", 0, scope="internal")+1
        symbols = var("symbols","*")
        symbol_style = var("symbol-style","html")

        # convert symbols to todo-list symbols
        def remap(s):
            s = s.strip()
            if symbol_style == "icons" or symbol_style == "icon":
                if s == "":
                    return "❑";
                elif s == "X":
                    return "x";
                elif s == "?":
                    return "question-mark";
                elif s == "v" or s == "V":
                    return "check";
                return s
            else:
                if s == "":
                    return "☐";
                elif s == "X" or s == "x":
                    return "☒";
                elif s == "v" or s == "V":
                    return "☑";
                return s


        symbols = [remap(s) for s in symbols]

        li_addition = ""
        if list_style == "auto":
            symb = symbols[0]
            if symb[0] == "+":
                classes.append("list-symbol-circ")
            elif symb[0] == "-":
                classes.append("list-symbol-line")
            else:
                li_addition = "data-icon='"+symb+"'"
        if list_style == "none":
            classes.append("list-symbol-none")
        elif list_style == "bullet" or list_style == "dot" or list_style=="auto-depth" and listdepth==1:
            pass
        elif list_style == "circ" or list_style=="auto-depth" and listdepth==2:
            classes.append("list-symbol-circ")
        elif list_style == "line" or list_style=="auto-depth" and listdepth>=3:
            classes.append("list-symbol-line")
        else:
            if isinstance(symbols,list):
                symb = symbols[0]
            else:
                symb = symbols
            if len(symb) == 1 and symb!="x":
                li_addition = "data-icon='"+symb+"'"
            else:
                li_addition = "class=\"oi-"+symb+"\""
        ret = html.make_main_tag(var, "ul", tag_style=style, tag_class=classes)
        list_content = var("content")
        if not isinstance(symbols,list):
            symbols = [symbols]*len(list_content)
        list_content_symb = symbols
        if len(list_content) > 0:
            list_content_symb += [list_content_symb[-1]]*(len(list_content) - len(list_content_symb))
            for li, symb in zip(list_content,list_content_symb):
                li_addition_local = li_addition
                if symb and symb not in "*-+":
                    if len(symb) == 1 and symb!="x":
                        li_addition_local = "class=\"icon-data \" data-icon='"+symb+"'"
                    else:
                        li_addition_local = "class=\"icon oi-"+symb+"\""

                if isinstance(li, dict) and li["type"] in ["ulist", "olist"]:
                    if li != list_content[0]:
                        ret = ret[:-5]
                    else:
                        ret += "<li>"
                    ret += run(li)
                    ret += "</li>"
                else:
                    ret += "<li "+li_addition_local+">"
                    ret += run(li,add_scope={"internal": {"listmode": True, "listdepth": listdepth}})
                    ret += "</li>"
        ret += "</ul>"
        return ret

    @apply_scope(insertBy="ref", insertFrom="link")
    def translate_link(self, var, run):
        href = var('dest',"")
        if href.endswith(".md") and var("md_link_replace",False,scope="internal"):
            href = href[:-2]+var("md_link_replace",scope="internal")
        content = run(var(['content', 'dest'], ""), add_scope={"internal": {"paragraphmode": True}})
        return html.make_main_tag(var, "a", tag_addition="href=\"{}\"", content="{}").format(href, content)

    @apply_scope()
    def translate_code_block(self, var, run):
        syntax = var(['syntax', 'code-syntax'], 'nohighlight')
        if syntax == "inject":
            return var('verbatim')
        verbatim = self.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var, run)
        whitespace = var('whitespace', '')
        if not var('notrim', False) and whitespace != '':
            verbatim = re.sub("^"+whitespace, "", verbatim)
            verbatim = re.sub("\n"+whitespace, "\n", verbatim)
        verbatim.replace("<","&lt;")
        verbatim.replace(">","&gt;")

        return html.make_main_tag(var, "pre", tag_style="margin:0", content="""<code class={1}>{0}</code>""") \
                .format(verbatim, syntax)

    @apply_scope()
    def translate_code_block_customsyntax(self, var, run):

        verbatim = ""
        verbatim_with_math = var("verbatim")

        # strip trailing spaces / newlines
        if isinstance(verbatim_with_math[0],str):
            if len(verbatim_with_math[0].strip()) == 0:
                verbatim_with_math = verbatim_with_math[1:]
            else:
                verbatim_with_math[0] = verbatim_with_math[0].strip()

        # replace escaped chars
        def replace(s):
            return s.replace("\{","{").replace("\}","}").replace("\\\\","\\")

        # parse all the math
        for item in verbatim_with_math:
            if isinstance(item, str):
                verbatim += replace(item)
            else:
                verbatim += "<span class=\"hljs-{0}\">{1}</span>".format(item["command"],"".join(replace(item["arguments"][0][0])))
        return html.make_main_tag(var, "pre", tag_style="margin:0", content="""<code class="hljs nohighlight">{0}</code>""") \
                .format(verbatim)


    @apply_scope()
    def translate_emph(self, var, run):
        return html.make_main_tag(var, "em", content="{}").format(run(var('text')))

    @apply_scope()
    def translate_strong(self, var, run):
        return html.make_main_tag(var, "strong", content="{}").format(run(var('text')))

    @apply_scope()
    def translate_bold(self, var, run):
        return html.make_main_tag(var, "b", content="{}").format(run(var('text')))

    @apply_scope()
    def translate_italic(self, var, run):
        return html.make_main_tag(var, "i", content="{}").format(run(var('text')))

    @apply_scope()
    def translate_strike(self, var, run):
        return html.make_main_tag(var, "s", content="{}").format(run(var('text')))

    @apply_scope(insertBy="ref", insertFrom="image")
    def translate_image(self, var, run):
        alt = run(var('alt_text', "")).strip()
        content = var('content','')
        title = run(content)
        width = var('width', "")
        width_lg = var('width_lg', width)
        width_md = var('width_md', width)
        width_sm = var('width_sm', width)
        width_xs = var('width_xs', width)
        if width_lg != "":
            width_lg = "width:"+str(width_lg)+"%;"
        if width_md != "":
            width_md = "width:"+str(width_md)+"%;"
        if width_sm != "":
            width_sm = "width:"+str(width_sm)+"%;"
        if width_xs != "":
            width_xs = "width:"+str(width_xs)+"%;"
        src = var('dest')

        # inline
        tag_class = html.get_classes(var,"")
        if len(title)==0 and not (isinstance(content,list) and len(content)!=0) and not var("block",False):
            return """
              <img src="{src}" class="figure-img img-fluid rounded d-none d-lg-inline {tag_class}" alt='{alt}' style="{width_lg}">
              <img src="{src}" class="figure-img img-fluid rounded d-none d-md-inline d-lg-none {tag_class}" alt='{alt}' style="{width_md}">
              <img src="{src}" class="figure-img img-fluid rounded d-none d-sm-inline d-md-none {tag_class}" alt='{alt}' style="{width_sm}">
              <img src="{src}" class="figure-img img-fluid rounded d-inline d-sm-none {tag_class}" alt='{alt}' style="{width_xs}">
            """.format(src=src, alt=alt, width_lg=width_lg, width_md=width_md,
                    width_sm=width_sm, width_xs=width_xs, tag_class=" ".join(tag_class))


        if var("card", False, scope="internal"):
            plain_body = """ style="padding: 0;" """ if var('plain', False) else ""
            return """
              <div class="card-body" {plain}>
                <figure class="figure text-center" style="display: block; margin: 0;">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-lg-inline" alt='{alt}' style="{width_lg}">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-md-inline d-lg-none" alt='{alt}' style="{width_md}">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-sm-inline d-md-none" alt='{alt}' style="{width_sm}">
                  <img src="{src}" class="figure-img img-fluid rounded d-inline d-sm-none" alt='{alt}' style="{width_xs}">
                  <figcaption class="figure-caption">{title}</figcaption>
                </figure>
              </div>
            """.format(src=src, alt=alt, title=title, plain=plain_body, width_lg=width_lg, width_md=width_md,
                    width_sm=width_sm, width_xs=width_xs)

        if var('plain', False):
            plain_body = """ style="padding: 0;" """ if var('plain', False) else ""
            plain_body_margin = """ style="margin-left: 0; margin-right: 0; border: 0;" """ if var('plain', False) else ""
            return html.make_main_tag(var, "div", tag_class="card", tag_addition="{plainmargin}", content="""
              <div class="card-body" {plain}>
                <figure class="figure text-center" style="display: block; margin: 0;">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-lg-inline" alt='{alt}' style="{width_lg}">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-md-inline d-lg-none" alt='{alt}' style="{width_md}">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-sm-inline d-md-none" alt='{alt}' style="{width_sm}">
                  <img src="{src}" class="figure-img img-fluid rounded d-inline d-sm-none" alt='{alt}' style="{width_xs}">
                  <figcaption class="figure-caption">{title}</figcaption>
                </figure>
              </div>
            """).format(src=src, alt=alt, title=title, plain=plain_body, plainmargin=plain_body_margin, width_lg=width_lg, width_md=width_md, width_sm=width_sm, width_xs=width_xs)
        return html.make_main_tag(var, "div", tag_class=["card", "bg-light"], content="""
          <div class="card-body">
            <figure class="figure text-center" style="display: block; margin: 0;">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-lg-inline" alt='{alt}' style="{width_lg}">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-md-inline d-lg-none" alt='{alt}' style="{width_md}">
                  <img src="{src}" class="figure-img img-fluid rounded d-none d-sm-inline d-md-none" alt='{alt}' style="{width_sm}">
                  <img src="{src}" class="figure-img img-fluid rounded d-inline d-sm-none" alt='{alt}' style="{width_xs}">
              <figcaption class="figure-caption">{title}</figcaption>
            </figure>
          </div>
        """).format(src=src, alt=alt, title=title, width_lg=width_lg, width_md=width_md, width_sm=width_sm, width_xs=width_xs) + """<div class="clearfix"></div>"""

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

        tablestr = html.make_main_tag(var, "table", tag_class=["table", "table-striped"])
        tablestr += """
          <thead>
            <tr>
        """

        for idx in range(cols):
            tablestr += "<th>{}</th>".format(run(header[idx]).strip())

        tablestr += """
            </tr>
          </thead>
        <tbody>
        """

        for row in table_content[2:]:
            assert len(row) == cols
            tablestr += "<tr>"
            for idx in range(cols):
                lgn = alignment[coltyp[idx]['align']]
                tablestr += """
                <td class="{align}">{content}</td>
                """.format(align=lgn, content=run(row[idx]))
            tablestr += "</tr>"

        tablestr += """
          </tbody>
        </table>
        """
        return tablestr

    @apply_scope()
    def translate_code_inline(self, var, run):
        syntax = var(['syntax', 'code-syntax'], 'nohighlight')
        verbatim = self.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var, run)
        return html.make_main_tag(var, "code", tag_class=["{}"], content="{}").format(syntax, verbatim)

    @apply_scope()
    def translate_quote(self, var, run):
        name = var("name", "")
        source = var("source", "")
        if source != "":
            source = '<cite title="{source}">{source}</cite>'.format(source=source)
        footer=""
        if name != "" or source != "":
            if name != "" and source != "":
                name += " in "
            footer = """
            <footer class="blockquote-footer">{name}{source}</footer>
            """.format(name=name,source=source)

        return html.make_main_tag(var, "blockquote", tag_class="blockquote", content="""
            <p class="mb-0">{content}</p>
            {footer}
        """).format(content=run(var('content')).strip(), footer=footer)

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def translate_footnote(self, var, run):
        footnotes_list = var("buffer",scope="footnotes")
        text = run(var('text'), add_scope={"internal": {"paragraphmode": True}}).strip()
        ref = var('ref','')
        index = len(footnotes_list)+1
        content = var('content')
        id = var('id', ref if ref != '' else "fn"+str(index))
        footnotes_list.append({'ref':ref,'text':text, 'content': content, 'index': index, 'id': id})
        footnote_type = var("footnote_type", "^")
        if footnote_type == "[]":
            footnote_text = "[{index}]"
        elif footnote_type == "^":
            footnote_text = "<sup>{index}</sup>"
        return html.make_main_tag(var, "span", tag_id=id, tag_class=["footnote",], content="{text}<a href=\"#"+id+"_content\">"+footnote_text+"</a>") \
            .format(text=text, index=index)

    @apply_scope(insertBy="ref", insertFrom="footnote")
    def translate_note(self, var, run):
        return html.make_main_tag(var, "span", tag_class=["btn-warning"], tag_addition='data-html="true" data-toggle="tooltip" title="{content}"', content="{text}") \
            .format(content=run(var('content'), add_scope={"internal": {"paragraphmode": True}}).replace('"',"'"), text=run(var('text'), add_scope={"internal": {"paragraphmode": True}}))

    @apply_scope()
    def translate_paragraph(self, var, run):
        repl = "{}"
        if var('alert', False):
            alert = var('alert', False)
            if isinstance(alert,bool):
                alert = 'info'
            return """<div class="alert alert-{alert}" role="alert">
                            {content}
                      </div>""".format(alert=alert, content=run(var('content')))

        if var("paragraphmode", False, scope="internal"):
            content = str(run(var('content')))
            content = content.strip()
            if content:
                return repl.format(content)
        else:
            content = str(run(var('content'), add_scope={"internal": {"paragraphmode": True}}))
            content = content.strip()
            if content:
                return str(html.make_main_tag(var, "p", content=repl)).format(content)

        return ""

    @apply_scope()
    def translate_indent(self, var, run):
        # TODO add tab Class
        return "<span class=\"tab\">{}</span>".format(run(var('content')))

    @apply_scope()
    def translate_url(self, var, run):
        return "<a href={dest}>{dest}</a>".format(dest=var("dest"))

    @apply_scope()
    def translate_hrule(self, var, run):
        return "<hr>"

    @apply_scope()
    def translate_softbreak(self, var, run):
        return "<br/>"

    @apply_scope()
    def translate_error(self, var, run):
        err = var("exception-object",None)
        err_type = var("exception-type")

        if err_type == "Syntax Error":
            text = var("text","")
            pos = var("pos","")
            err = text + "\n\n" + str(pos)

            # get error source
            add_range = 1
            file_path = var("absolute_path")
            file_error_source = []
            for i in range(pos[1]-add_range,pos[3]+add_range+1):
                line_number = {
                    "arguments": [["Line "+str(i)+": "]],
                    "command": "comment",
                    "type": "latex_command"
                }
                file_error_source.append(line_number)

                line = linecache.getline(file_path, i)
                if i < pos[3] or i > pos[3]:
                    file_error_source.append({
                        "arguments": [[line]],
                        "command": "comment",
                        "type": "latex_command"
                    })
                elif i == pos[3] and i == pos[1]:
                    file_error_source.append(line[:pos[2]])
                    file_error_source.append({
                        "arguments": [[line[pos[2]:pos[4]+1]]],
                        "command": "title",
                        "type": "latex_command"
                    })
                    file_error_source.append(line[pos[4]+1:])
                elif i == pos[1]:
                    file_error_source.append(line[:pos[2]])
                    file_error_source.append({
                        "arguments": [[line[pos[2]:]]],
                        "command": "title",
                        "type": "latex_command"
                    })
                elif i - add_range == pos[3]:
                    file_error_source.append({
                        "arguments": [[line[:pos[4]+1]]],
                        "command": "title",
                        "type": "latex_command"
                    })
                    file_error_source.append(line[pos[2]:])
                else:
                    file_error_source.append(line)
            # file_error_source[0] = file_error_source[0][pos[2]:]
            # file_str = "".join(file_error_source)
            # code_block = {"type": "code_block", "verbatim":file_str}
            code_block = {
                        "customsyntax": True,
                        "type": "math_block",
                        "verbatim": file_error_source,
                        # [
                            # "\n#include <iostream>\nusing namespace std;\nint main()\n",
                            # "{",
                            # "\n    unsigned int n;\n    unsigned long long factorial = 1;\n\n    ",
                            # {
                            #     "arguments": [
                            #         [
                            #             "cout << \"Enter a positive integer: \";"
                            #         ]
                            #     ],
                            #     "command": "meta",
                            #     "type": "latex_command"
                            # },
                            # "\n    cin >> n;\n\n    ",
                            # {
                            #     "arguments": [
                            #         [
                            #             "for(int i = 1; i <=n; ++i) {"
                            #         ]
                            #     ],
                            #     "command": "title",
                            #     "type": "latex_command"
                            # },
                            # "\n        ",
                            # {
                            #     "arguments": [
                            #         [
                            #             "factorial *= i;"
                            #         ]
                            #     ],
                            #     "command": "keyword",
                            #     "type": "latex_command"
                            # },
                            # "\n    ",
                            # {
                            #     "arguments": [
                            #         [
                            #             "}"
                            #         ]
                            #     ],
                            #     "command": "title",
                            #     "type": "latex_command"
                            # },
                            # "\n\n    ",
                            # {
                            #     "arguments": [
                            #         [
                            #             "cout << \"Factorial of \" << n << \" = \" << factorial;"
                            #         ]
                            #     ],
                            #     "command": "meta",
                            #     "type": "latex_command"
                            # },
                            # "\n    return 0;\n",
                            # "}",
                            # "\n"
                        # ]
                    }


            content = [
                "An Error occured during parsing ",
                "the File '",file_path,"'.",
                {"type":"hard break"},
                "The Error says: '",
                {"type":"strong","text":text},
                "'.",
                {"type":"hard break"},
                {
                    "type": "section",
                    "collapsible": True,
                    "show": True,
                    "title": ["Wrong Symbol ",pos[0]," between Line ",pos[1], " Character ",pos[2]," and Line ",pos[3], " Character ",pos[4],"."
                    ],
                    "h-level": 0,
                    "content": code_block
                }
            ]
        else:
            if isinstance(err,Exception):
                err = traceback.format_exc()
            content = [
                "An Error occured during translation in '"+self.__class__.__name__+"'-View",
                {"type":"hard break"},
                {
                    "type": "section",
                    "collapsible": True,
                    "title": "Traceback",
                    "h-level": 0,
                    "content": {"type": "code_block", "verbatim":err}
                }
            ]

        adict = {
            "type": "section",
            # "collapsible": True,
            "alert": "danger",
            "title": err_type,
            "h-level": 0,
            "content": content
        }
        return run(adict)


    # ====================== #
    # preconfigured commands #
    # ====================== #
    @apply_scope()
    def cmd_n(self, var, run):
        return "<br>\n"

    @apply_scope(getVars=["iconname"])
    def cmd_icon(self, var, run, iconname):
        return "<span class=\"oi oi-{icon}\" title=\"{icon}\" aria-hidden=\"true\"></span>&nbsp;".format(icon=iconname)

    @apply_scope(insertBy="ref", insertFrom="footnote", getVars=["clear"])
    def cmd_footnotes(self, var, run, clear=False):
        footnotes_list = var("buffer",scope="footnotes")
        if len(footnotes_list)==0:
            return ""
        if clear:
            footnotes_list.clear()
            return ""
        footnote_view_content = [ [str_escaped("[<span id=\""+f["id"]+"_content\">"+str(f["index"])+"</span>] "),MLList(f["content"]), {"type":"new line"}] for f in footnotes_list ]
        footnotes_list.clear()
        footnote_view = [{"type": "hard break"}, {"type": "hrule"}, {"type": "hard break"},
            {
                "content": footnote_view_content,
                "scope": {},
                "type": "paragraph"
            }]
        return run(footnote_view)

    @apply_scope(getVars=["scopes"])
    def cmd_clearcounter(self, var, run, scopes):
        # create new counter
        if "counter" not in scopes[-1]:
            scopes[-1]["counter"] = dict()
        scopes[-1]["counter"] = []
        return ""

    @apply_scope(getVars=["href"])
    def cmd_redirect(self, var, run, href):
        if href.endswith(".md") and var("md_link_replace",False,scope="internal"):
            href = href[:-2]+var("md_link_replace",scope="internal")
        return """
            <meta http-equiv="refresh" content="0; url={href}" />
        """.format(href=href)

    @apply_scope(getVars=["scopes","clear","maxdepth","nested","create","filename"])
    def cmd_contentlist(self, var, run, scopes, clear=False,maxdepth=-1,nested=False, create=False, filename=""):
        if clear:
            var("contentlist",scope="internal").clear()
            return ""

        if create:
            # create new content list
            if "internal" not in scopes[-1]:
                scopes[-1]["internal"] = dict()
            scopes[-1]["internal"]["contentlist"] = []
            return ""

        contentlist = var("contentlist",scope="internal")

        def deferred(q,i,cl):
            content = {"type":"ulist","list-symbol":"custom","symb":["--" for counter,id,title,livel in cl for c in counter], "content":
                    [[[".".join([str(c) for c in counter]) + ". "] if counter != [] and counter != [0] else [],{"type":"link","dest": filename+"#"+id, "content": re.sub('<[^<]+?>', '', title)}] for counter,id,title,level in cl if (maxdepth == -1 or len(counter)<=maxdepth)]
            }

            q.put((i,run(content)))

        t = threading.Thread(target=deferred, args = (self.thread_queue,self.thread_num,contentlist))
        t.daemon = True
        self.thread_later_start[self.thread_num] = t
        self.thread_num += 1

        return "{{thread_"+str(self.thread_num-1)+"}}"

        return ""
        callee = var("callee",scope="internal",ignore_scopes=levelup)
        s = ""
        def walk(tree, depth=1):
            s_walk = ""
            autoid = var("section-auto-id",True)
            for t in tree:
                if not isinstance(t,dict):
                    continue
                if t["type"] == "section":
                    if "id" not in t and autoid:
                        t["id"] = View.rawtext(t["title"]).strip().replace(" ","-")

                    if "id" in t:
                        s_walk += "<li><a href=\"#"+t["id"]+"\">"+run(t["title"])+"</a></li>"
                    else:
                        s_walk += "<li>"+run(t["title"])+"</li>"
                if "content" in t and (maxdepth == -1 or depth<maxdepth):
                    s_walk += walk(t["content"], depth+1)
            return "<ol>"+s_walk+"</ol>"
        return walk(callee)





    def __init__(self,*args,**settings):
        super().__init__(*args,**settings)
        self.defaults = {**self.defaults, **settings}

        self.viewname = self.__class__.__name__
        self.filesuffix = ".html"
        self.defaulttheme = "vc_style"
        self.mathinline_template = "\({}\)"
        self.mathblock_template = "\[{}\]"

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
            'new line': self.translate_softbreak,
            'error': self.translate_error,
        })

        self.typelator.update({
            'str_escaped': self.handle_str
        })

        # add extra styles
        self.translate_styles.update({
            "card": {"card": True},
            "collapsible": {"collapsible": True}
        })

        # add counters for the following elements
        self.counters = ["section", "equation"]


        self.unique_hashes = {}




    # ====== #
    # Styles #
    # ====== #

    @apply_scope()
    def translate_card_table(self, var, run):
        alignment = {
            'centered': "text-center",
            'center': "text-center",
            'normal': "text-left",
            'left': "text-left",
            'right': "text-right"
        }
        table_content = var('content')

        def convert_card(card, card_settings):
            tag_class = ["card"]
            tag_style = []
            if var("plain", False):
                 tag_style.append("border:0; margin-left:0; margin-right:0")
            if "align" in card_settings:
                tag_class.append(alignment[card_settings['align']])
            card = strip_empty(card)
            if "header" in card_settings and card_settings["header"] or var("withheader",False):
                return run({**card_settings,"type":"section","card":True,"content":card[4:],"title":[card[0]],"subtitle":[card[2]],"h-level":0, "plain":var("plain",False), "cardheader": var("cardheader", False)})
            return html.make_tag(var,"div", tag_class=tag_class, tag_style=tag_style, content="<div class=\"card-body\">"+run(MLList(card),add_scope={"internal": {"card": True}})+"</div>")

        def strip_empty(card):
            for c in range(len(card)-1,0,-1):
                if isinstance(card[c],dict) and card[c]["type"] in ["hard break","new line"]:
                    card = card[:c]+card[c+1:]
                else:
                    break
            return card

        card_table = []
        cards = []
        cards_settings = []
        for idx, row in enumerate(table_content):

            # make new row
            if isinstance(row[0],dict) and row[0]["type"] == "table_separator":
                if len(cards) != 0:
                    card_table.append("<div class=\"card-deck\">"+"\n".join([convert_card(c,s) for c,s in zip(cards,cards_settings)])+"</div>")
                    if var("plain", False) and "line" in row[0] and row[0]["line"]:
                        card_table.append("<hr>")
                    cards = []
                    cards_settings = []

                for card in row:
                    if idx == len(table_content) - 1 and card['type'] == "table_separator":
                        continue
                    cards.append([])
                    cards_settings.append(card)

            elif len(cards)==0:
                for card in row:
                    cards.append([])

            else:
                for i, card in enumerate(row):
                    if len(card)>0:
                        cards[i].append(card)
                        cards[i].append({"type":"new line"})
                        # if len(card) > 0 and isinstance(card[-1],str) and card[-1].endswith("  "):
                    else:
                        # cards[i].append({"type":"new line"})
                        cards[i].append({"type":"hard break"})

        if len(cards) != 0:
            card_table.append("<div class=\"card-deck\">"+"\n".join([convert_card(c,s) for c,s in zip(cards,cards_settings)])+"</div>")

        if var("plain",False):
            return "\n".join(card_table)
        return "\n<br>".join(card_table)

        # # the section may be a card-group
        # # https://getbootstrap.com/docs/4.0/components/card/#card-groups
        # if var('carddeck', False):
        #     return "\n".join([
        #         html.make_main_tag(var, "div", tag_class="card", tag_addition="{plainmargin}", content="""
        #           <div class="card-header {hidden}">
        #             {title}
        #           </div>
        #           <div class="card-body" {plain}>
        #             <div class="card-deck">
        #               {content}
        #             </div>
        #           </div>
        #         """).format(
        #             content=run(var('content'), add_scope={"internal": {"paragraphmode": True}}), title=run(title),
        #             hidden=hidden, plain=plain_body, plainmargin=plain_body_margin
        #         ),
        #         run({'type': 'hard break'})  # TODO can we invoke method instead?
        #     ])

    @apply_scope()
    def translate_card_paragraph(self, var, run):
        repl = "{}"
        if var('alert', False):
            alert = var('alert', False)
            if isinstance(alert,bool):
                alert = 'info'
            return """<div class="alert alert-{alert}" role="alert">
                            {content}
                      </div>""".format(alert=alert, content=run(var('content')))

        # the paragraph may be a card/box whatever
        plain_body = """ style="padding: 0;" """ if var('plain', False) else ""
        plain_body_margin = """ style="margin-left: 0; margin-right: 0; border: 0;" """ if var('plain', False) else ""
        text_right = "text-right" if var('text-right', False) else ""
        text_center = "text-center" if var('text-center', False) else ""
        alignment = text_center if text_center else text_right
        title = var('title', "")
        titlestr = ""
        if title:
            titlestr = """<h3 class="card-title">{}</h3>""".format(title)
        subtitle = var('subtitle', "")
        subtitlestr = ""
        if subtitle:
            subtitlestr = """<h5 class="card-subtitle mb-2 text-muted">{}</h5>""".format(subtitle)
        mutebody = "hidden" if var('mutebody', False) else ""
        repl = """
        <div class="card {alignment}" {plainmargin}>
          <div class="card-body" {plain}>
            {title}
            {subtitle}
            <span class="card-text {hidden}">{{}}</span>
          </div>
        </div>
        """.format(
            title=titlestr, subtitle=subtitlestr,
            hidden=mutebody, alignment=alignment,
            plain=plain_body, plainmargin=plain_body_margin
        )

        content = str(run(var('content')))
        content = content.strip()
        if content:
            return repl.format(content)


    @apply_scope()
    def translate_card_section(self, var, run):
        alignment = {
            'centered': "text-center",
            'center': "text-center",
            'normal': "text-left",
            'left': "text-left",
            'right': "text-right"
        }
        align = alignment[var("align","normal")]
        title = var('title')
        subtitle = var('subtitle',"")
        level = var('h-level')

        title_str = run(title).encode('utf-8')

        hidden = "hidden" if var('hidden', False) else ""
        plain_body = """ style="padding: 0;" """ if var('plain', False) else ""
        plain_body_margin = """ style="margin-left: 0; margin-right: 0; border: 0;" """ if var('plain', False) else ""

        widthstr = ""
        width = int(var('width', 0))
        if width:
            widthstr = "w-" + str(width)

        title_addition = ""

        if var("card",False,scope="internal"):
            if (var("cardheader",False)):
                return html.make_tag(var, "div", tag_class=["card", "width"], tag_addition="{plainmargin}", content="""
                  <div class="card-header {align}" {plain}>
                    {title}
                  </div>
                  <div class="card-body {align}" {plain}>
                    {content}
                  </div>
                """).format(
                    title=run(title)+title_addition, content=run(var('content'), add_scope={"internal": {"paragraphmode": True}}),
                    plain=plain_body, plainmargin=plain_body_margin,
                    width=widthstr, align=align, subtitle=run(subtitle)
                )
            else:
                return html.make_tag(var, "div", tag_class=["card", "width"], tag_addition="{plainmargin}", content="""
                  <div class="card-body {align}" {plain}>
                    <h3 class="card-title">{title}</h3>
                    <h5 class="card-subtitle mb-2 text-muted">{subtitle}</h5>
                    <span class="card-text">{content}</span>
                  </div>
                """).format(
                    title=run(title)+title_addition, content=run(var('content'), add_scope={"internal": {"paragraphmode": True}}),
                    plain=plain_body, plainmargin=plain_body_margin,
                    width=widthstr, align=align, subtitle=run(subtitle)
                )

        # the section may be a card
        # https://getbootstrap.com/docs/4.0/components/card/
        return "\n".join([
            html.make_main_tag(var, "div", tag_class=["card", "width"], tag_addition="{plainmargin}", content="""
              <div class="card-header {hidden}">
                {title}
              </div>
              <div class="card-body" {plain}>
                {content}
              </div>
            """).format(
                title=run(title), content=run(var('content'), add_scope={"internal": {"paragraphmode": True}}),
                hidden=hidden, plain=plain_body, plainmargin=plain_body_margin,
                width=widthstr
            ),
            run({'type': 'hard break'})  # TODO can we invoke method instead?
        ])

    @apply_scope()
    def translate_card_code_block(self, var, run):
        syntax = var(['syntax', 'code-syntax'], 'nohighlight')
        verbatim = self.replace_in_verbatim(var('verbatim'), var(['replace', 'code-replace'], {}), var, run)
        whitespace = var('whitespace', '')
        if not var('notrim', False) and whitespace != '':
            verbatim = re.sub("^"+whitespace, "", verbatim)
            verbatim = re.sub("\n"+whitespace, "\n", verbatim)

        title = var('title', "")
        titlestr = ""
        if title:
            titlestr = """<h4 class="card-title">{}</h4>""".format(title)
        subtitle = var('subtitle', "")
        subtitlestr = ""
        if subtitle:
            subtitlestr = """<h6 class="card-subtitle mb-2 text-muted">{}</h6>""".format(subtitle)
        repl = html.make_main_tag(var, "div", tag_class="card-body", content="""
            {title}
            {subtitle}
            <span class="card-text">{repl}</span>
        """).format(
            title=titlestr, subtitle=subtitlestr, repl=html.make_tag(var, "pre", tag_style="margin:0", content="""<code class="{1}">{0}</code>"""), \
        )
        return repl.format(verbatim, syntax)


    # ----------- #
    # Collapsible #
    # ----------- #
    @apply_scope()
    def translate_collapsible_section(self, var, run):
        title = var('title')
        level = var('h-level')
        counter = var('section',scope='counter')

        title_str = run(title).encode('utf-8')
        hidden = "hidden" if var('hidden', False) else ""
        plain_body = """ style="padding: 0;" """ if var('plain', False) else ""
        plain_body_margin = """ style="margin-left: 0; margin-right: 0; border: 0;" """ if var('plain', False) else ""

        title_addition = ""

        if var('section-counter',False):
            counter[-1]+=1;
            counter_str = ".".join([str(c) for c in counter])+". "
        else:
            counter_str = ""

        id = View.rawtext(title).strip().replace(" ","-") if var("section-auto-id",True) and not var("id",False) else ""
        title_str = run(title).encode('utf-8')




        # the section may be collapsible
        # https://getbootstrap.com/docs/4.0/components/collapse/
        idhash = "collapse"+hashlib.sha512(title_str).hexdigest()[0:10]
        while idhash in self.unique_hashes:
            idhash += "0"
        self.unique_hashes[idhash] = 0
        show = var('show', '')
        if show:
            show = "show"
        return "\n".join([
            html.make_main_tag(var, "div", tag_class="card", tag_addition="{plainmargin}", content="""
              <a class="card-header {hidden}" style="cursor: pointer;" data-toggle="collapse" data-target="#{hash}" aria-expanded="{ariaexpanded}" aria-controls="{hash}">
                {counter}{title}
              </a>
              <div class="collapse {show}" id="{hash}">
                  <div class="card-body" {plain}>
                    {content}
                  </div>
              </div>
            """).format(
                hash=idhash, size=(level + 1),
                title=run(title)+title_addition, content=run(var('content'), add_scope={"internal": {"paragraphmode":
                    True}, "counter": {"section": counter+[0]}}),
                hidden=hidden, plain=plain_body, plainmargin=plain_body_margin,
                show=show, counter=counter_str, ariaexpanded=True if show=="show" else False
            ),
            run({'type': 'hard break'})  # TODO can we invoke method instead?
        ])



    # ====== #
    # Themes #
    # ====== #
    def listThemes(self):
        # theme_list = super().listThemes()

        theme_list = []
        theme_path = os.path.join(defaults["theme_path"],self.viewname)
        if os.path.isdir(theme_path):
            theme_list += [(o,os.path.join(theme_path,o)) for o in os.listdir(theme_path)]
        theme_list += [(modname, "preinstalled") for importer, modname, ispkg in pkgutil.iter_modules(luke.themes.html.__path__)]

        themes = []
        for themename, path in theme_list:

            if path == "preinstalled":
                path = os.path.join(luke.themes.__path__[0],themename)

            themes.append((themename+"."+self.viewname,path))
        return themes

    def installTheme(self, theme_name, theme_path=defaults["theme_path"], reinstall=True):
        theme_path = os.path.join(theme_path,self.viewname)
        if os.path.isdir(theme_path) and not reinstall:
            print("Theme "+theme_name+" is already installed under "+themepath)
            return

        # load installer
        try:
            theme = __import__("luke.themes."+self.viewname+"."+theme_name, fromlist=['']).Theme
        except:
            print("There is no such theme '"+theme_name+"'")
            return
        theme.install(theme_path)


    def guess_tree_theme(self,tree,settings,attr_name="theme"):
        theme = "default"
        if settings["overwrite_theme"]:
            theme = settings["theme_name"]
        else:
            found = False
            for b in tree["content"]:
                if isinstance(b,dict) and "type" in b and b["type"]=="attributes":
                    if attr_name in b:
                        found = True
                        theme = b[attr_name]
                    else:
                        break
                if not found:
                    theme = settings["theme_name"]

        # get default theme
        if theme == "default":
            theme = settings["default_"+self.__class__.__name__+"_theme"]

        return theme

    def run(self,tree,**settings):
        linecache.clearcache()

        treevar = lambda var,alt: tree["scope"]["variable"][var] if "scope" in tree and "variable" in tree["scope"] and var in tree["scope"]["variable"] else alt
        classname = self.__class__.__name__


        # ---------------------- #
        # parse in-file settings #
        # ---------------------- #
        settings = {**defaults, **self.defaults, **settings}
        theme = self.guess_tree_theme(tree,settings)
        theme_variant = self.guess_tree_theme(tree,settings,"theme-variant")
        settings["theme"] = theme
        settings["theme_variant"] = theme_variant

        # get theme resources
        path_theme = os.path.join(settings["theme_path"],classname,theme)
        path_resources_src = os.path.join(settings["theme_path"],classname,theme,"resources")


        if not settings["to_string"]:

            # ---------------- #
            # parse shorthands # - for file saving
            # ---------------- #
            cwd = os.getcwd()
            path_file = treevar("absolute_path","./file.md")

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
            outfilename = os.path.join(path_out,os.path.basename(os.path.splitext(path_file)[0]) + ".html")

        else:
            path_resources_relative = settings["resources_relative"]

        # ---------------------- #
        # parse in-file settings #
        # ---------------------- #

        # where to find resources when viewing from inside html-document
        resources_relative = treevar("resources_relative",path_resources_relative)

        if settings["resources_relative_append_theme"]:
            resources_relative = os.path.join(resources_relative,classname,theme,"resources")


        # ------------------ #
        # parse content-tree #
        # ------------------ #
        content = super().run(tree,**settings)


        # ------------------------ #
        # get theme resource paths #
        # ------------------------ #
        try:
            themecls = __import__("luke.themes."+classname+"."+theme, fromlist=['']).Theme
            resource_paths_dict = themecls.get_resource_paths(False if "cdn" in settings and settings["cdn"] else resources_relative)
        except ModuleNotFoundError:
            resource_paths_dict = {}


        # ------------------- #
        # get header & footer #
        # ------------------- #

        path_header = os.path.join(path_resources_src,"header.html")
        path_footer = os.path.join(path_resources_src,"footer.html")

        # formatter dict
        fdict = format_dict(**{
            "resources":resources_relative,
            "theme": theme,
            "theme-variant": theme_variant,
            "components": format_dict(**tree["global_scope"]["components"]) if "global_scope" in tree and "components" in tree["global_scope"] else format_dict()
        }, **resource_paths_dict)

        # use from copied resource if overwritten
        # else use original file from package
        try:
            if os.path.exists(path_header):
                with open(path_header, "r") as header:
                    header = header.read().format(**fdict).encode("utf-8")
            else:
                header = pkgutil.get_data("luke.themes."+classname+"."+theme,"header.html").decode("utf-8")
                header = header.format(**fdict).encode("utf-8")

            # same with footer-file
            if os.path.exists(path_footer):
                with open(path_footer, "r") as footer:
                    footer = footer.read().format(**fdict).encode("utf-8")
            else:
                footer = pkgutil.get_data("luke.themes."+classname+"."+theme,"footer.html").decode("utf-8")
                footer = footer.format(**fdict).encode("utf-8")
        except KeyError:
            raise KeyError("Tried to find key in formatting dictionary that does not exist.")

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

        # copy resource folder if not yet done
        if settings["copy_resources"] and not os.path.exists(path_resources_dest):
            if settings["verbose"] >= 1:
                print("Copying resources to: "+path_resources_dest)
            if os.path.exists(path_resources_src):
                shutil.copytree(path_resources_src, path_resources_dest)
            else:
                raise ValueError("The resource-directory '"+path_resources_src+"' does not exist and thus cannot be copied.")

View = html
