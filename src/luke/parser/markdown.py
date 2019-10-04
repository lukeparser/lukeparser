#!/usr/bin/env python
"""
Markdown parser
"""
from bison import BisonParser, BisonSyntaxError
import os


# Multiline-List
class MLList(list):
    pass


class attr_dict(dict):
    pass


class MarkdownParser(BisonParser):
    """
    Implements a markdown parser. Grammar rules are defined in the method
    docstrings. Scanner rules are in the 'lexscript' attribute.
    """

    def run(self,**kwargs):
        self.last_list = []
        tree = super().run(**kwargs)
        return tree

    def __init__(self, **kwargs):

        # Declare the start target here (by name)
        # And additional options to the grammar
        self.start = "input_start"
        self.options = ["%define api.pure full", "%define api.push-pull push","%lex-param {yyscan_t scanner}","%parse-param {yyscan_t scanner}", "%define api.value.type {void *}"] #, "%define parse.error verbose"]

        # ----------------------------------------------------------------
        # lexer tokens - these must match those in your lex script (below)
        # ----------------------------------------------------------------
        self.tokens = [

            # [State] HYPERREF
            'FOOTNOTE_START', 'FOOTNOTE_MID', 'FOOTNOTE_INLINE_START', 'FOOTNOTE_INLINE_MID', 'IMG_START', 'LINK_START', 'HYPERREF_LINK_CHAR', 'HYPERREF_LINK_ALT_CHAR', 'HYPERREF_LINK_ALT_END', 'HYPERREF_LINK_ALT_START',
            'HYPERREF_LINK_END', 'HYPERREF_LINK_MID', 'LINK_DEFINITION', 'IMAGE_DEFINITION', 'FOOTNOTE_DEFINITION', 'HYPERREF_REF_MID', 'HYPERREF_REF_END',
            'HYPERREF_CODE_START', 'HYPERREF_CODE_CHAR', 'HYPERREF_CODE_END',

            # STRUCTURAL SYMBOLS
            'HEADINGHASH', 'HEADINGHASH_END', 'HEADING_ULINEDBL', 'HEADING_ULINESGL', 'ULIST_SYM', 'OLIST_SYM',
            'QUOTE_SYM', 'INDENT_SYM',

            # MARKUP
            'EMPH_START', 'EMPH_END', 'STRONG_START', 'STRONG_END', 'STRIKE_START', 'STRIKE_END',
            'ITALIC_START', 'ITALIC_END', 'BOLD_START', 'BOLD_END',

            # STRUCTURAL
            'BR', 'CHAR', 'NEWLINE',

            # [State] ATTRIBUTE
            'ATTR_START', 'ATTR_END', 'ATTR_END_AND_ARG_START', 'ATTR_INPUT',
            'ATTR_HASH', 'ATTR_DOT', 'ATTR_EXCLAMATION', 'ATTR_COMMA', 'ATTR_EQUAL', 'ATTR_BOOLEAN', 'ATTR_NUMBER', 'ATTR_STRING',
            'ATTR_WORD', 'ATTR_PLACEHOLDER',

            # [State] Codeblock, Mathblock
            'CODEBLOCK_START', 'CODEBLOCK_END', 'CODEBLOCK_STRING_BEFORE', 'CODEBLOCK_BR', 'CODEBLOCK_CHAR',
            'CODEINLINE_START', 'CODEINLINE_CHAR', 'CODEINLINE_END',
            'MATHBLOCK_START', 'MATHINLINE_START', 'MATHBLOCK_CHAR', 'MATH_END',

            # Table
            'TABLE_DELIM', 'TABLE_HRULE', 'TABLE_HRULE_CENTERED', 'TABLE_HRULE_LEFT_ALIGNED',
            'TABLE_HRULE_RIGHT_ALIGNED',

            # Latex (normal-mode)
            'LATEX_COMMAND', 'LATEX_COMMAND_WITH_ARGUMENTS', 'PLACEHOLDER', 'LATEX_COMMAND_WITH_OPTIONAL_ARGUMENT',
            'MATHBLOCK_LATEX_COMMAND', 'MATHBLOCK_CURLY_OPEN', 'MATHBLOCK_CURLY_CLOSE', 'MATHBLOCK_VERBATIM_PLACEHOLDER',

            # other
            'URL', 'HRULE', 'UNEXPECTED_END'

        ]

        # ------------------------------
        # precedences
        # ------------------------------
        self.precedences = ()

        # $$
        # -----------------------------------------
        # raw lex script, verbatim here
        # -----------------------------------------

        self.lexscript = r"""
        %option yylineno
        %option reentrant bison-bridge bison-locations
        %option header-file="lex.yy.h"
        %option never-interactive
        %option extra-type="int"

        %{
        #include "tokens.h"

        // chars to replace
        const char *chr_sqr_open = (char *)"[\0";
        const char *chr_sqr_close = (char *)"]\0";
        const char *chr_curly_open = (char *)"{\0";
        const char *chr_bs_curly_open = (char *)"\\{\0";
        const char *chr_curly_close = (char *)"}\0";
        const char *chr_bs_curly_close = (char *)"\\}\0";
        const char *chr_hash = (char *)"#\0";
        const char *chr_star = (char *)"*\0";
        const char *chr_tri_close = (char *)">\0";
        const char *chr_tri_open = (char *)"<\0";
        const char *chr_minus = (char *)"-\0";
        const char *chr_underscore = (char *)"_\0";
        const char *chr_dollar = (char *)"$\0";
        const char *chr_backtick = (char *)"`\0";
        const char *chr_backslash = (char *)"\\\0";
        const char *chr_bs_backslash = (char *)"\\\\\0";
        const char *chr_pipe = (char *)"|\0";
        const char *chr_emdash = (char *)"\xE2\x80\x94\0";
        const char *chr_space = (char *)" \0";
        const char *chr_newline = (char *)"\n\0";

        // attribute/input-stack
        // printf("Push State -> index:%d state:%d\n",ais_i,state);
        // printf("Current State -> index:%d state:%d\n",ais_i,ais[ais_i]);
        int ais[10000];
        int ais_i = -1;
        #define STATE_PUSH(state) \
            ais_i++; \
            ais[ais_i] = state; \
            BEGIN(state);

        #define STATE_POP() \
            ais_i--; \
            if(ais_i<0) { \
                ais_i = -1; \
                BEGIN(INITIAL);  \
            } else { \
                BEGIN(ais[ais_i]); \
            }


        // emph strong strike - state
        char ess[5] = {0,0,0,0,0};
        int ess_i = 0;
        #define ess_state_stack(char,start_sym,end_sym) \
            if(ess_i==0 || ess[ess_i-1] != char) { \
                ess[ess_i] = char; \
                ess_i++; \
                returntoken(start_sym);  \
            } else { \
                ess_i--; \
                returntoken(end_sym); \
            }

        #define reset_stacks() \
                ais_i=-1; \
                ess_i=0;

        #define YY_USER_ACTION                                                     \
          yylloc->first_line = yylloc->last_line;                                  \
          yylloc->first_column = yylloc->last_column;                              \
          if (yylloc->first_line == yyget_lineno(yyscanner))                       \
             yylloc->last_column += yyget_leng(yyscanner);                         \
          else {                                                                   \
             int col;                                                              \
             for (col = 1; yyget_text(yyscanner)[yyget_leng(yyscanner) - col] != '\n'; ++col) {}                                  \
             yylloc->last_column = col;                                            \
             yylloc->last_line = yyget_lineno(yyscanner);                          \
          }


        #include <stdio.h>
        #include <string.h>
        #include "Python.h"
        #include "tokens.h"
        extern void *py_parser;
        extern void (*py_input)(PyObject *parser, char *buf, int *result, int max_size);

        PyMODINIT_FUNC PyInit_markdown_parser(void) { /* windows needs this function */ }

        // https://stackoverflow.com/questions/42434603/how-can-flex-return-multiple-terminals-at-one-time
        #define returntoken(tok)                                       \
                *yylval = (void*)PyUnicode_FromString(strdup(yytext)); \
                return tok;
        #define returntokenFromString(str, tok)                        \
                *yylval = (void*)strdup(str);                          \
                return tok;
        #define YY_INPUT(buf,result,max_size) {                        \
            (*py_input)(py_parser, buf, &result, max_size);            \
        }
        %}

        u2a     [\xC2-\xDF][\x80-\xBF]
        u2b     \xE0[\xA0-\xBF][\x80-\xBF]
        u3a     [\xE1-\xEC\xEE\xEF][\x80-\xBF]{2}
        u3b     \xED[\x80-\x9F][\x80-\xBF]
        u4a     \xF0[\x90-\xBF][\x80-\xBF]{2}
        u4b     [\xF1-\xF3][\x80-\xBF]{3}
        u4c     \xF4[\x80-\x8F][\x80-\xBF]{2}
        utf_8   {u2a}|{u2b}|{u3a}|{u3b}|{u4a}|{u4b}|{u4c}
        any     {utf_8}|.
        indent  (" "" "+|\t)
        whitespace [ \t]*
        whitespace_nl [ \t\n]*
        word    [a-zA-Z][0-9a-zA-Z_\-]*
        placeholder {word}(\.{word})*

        %s EMPH_STATE STRONG_STATE STRIKE_STATE

        %x ML_COMMENT COMMENT CODEBLOCK_STATE CODEBLOCK_STATE_VERBATIM CODEINLINE_STATE MATHINLINE_STATE ATTRIBUTE_STATE HYPERREF_LINK_STATE HYPERREF_DEFINITION HEADINGHASH_STATE HYPERREF_CODE_STATE HYPERREF_LINK_ALT_STATE
        %%
            if (yyget_extra(yyscanner)) {
                  return 0;
            }
            yyset_extra(0,yyscanner);

        <INITIAL>{whitespace}"/*"               { STATE_PUSH(ML_COMMENT); }
        <ML_COMMENT>"/*"                        { STATE_PUSH(ML_COMMENT); }
        <ML_COMMENT>"*/"                        { STATE_POP(); }
        <ML_COMMENT>\n+                         { }
        <ML_COMMENT>{any}                       { }
        <INITIAL>"//"                           { STATE_PUSH(COMMENT); }
        <COMMENT>./\n                           { STATE_POP(); }
        <COMMENT>{any}                          { }

        ^" "" "+\n                              { returntoken( BR ); }
        " "" "+\n                               { returntoken( NEWLINE ); }
        ("https://"|"ftp://"|"http://"|"www.")[^\]\n ]+   { returntoken(URL); }
        \<("https://"|"ftp://"|"http://"|"www.")[^\>\]]+\> { returntoken(URL); }

        "\\["                                   { returntokenFromString(chr_sqr_open, CHAR); }
        "\\]"                                   { returntokenFromString(chr_sqr_close, CHAR); }
        "\\{"                                   { returntokenFromString(chr_curly_open, CHAR); }
        "\\}"                                   { returntokenFromString(chr_curly_close, CHAR); }
        "\\#"                                   { returntokenFromString(chr_hash, CHAR); }
        "\\*"                                   { returntokenFromString(chr_star, CHAR); }
        "\\-"                                   { returntokenFromString(chr_minus, CHAR); }
        "\\_"                                   { returntokenFromString(chr_underscore, CHAR); }
        "\\$"                                   { returntokenFromString(chr_dollar, CHAR); }
        "\\|"                                   { returntokenFromString(chr_pipe, CHAR); }
        "\\`"                                   { returntokenFromString(chr_backtick, CHAR); }
        "\\\\"                                  { returntokenFromString(chr_backslash, CHAR); }
        "--"                                    { returntokenFromString(chr_emdash, CHAR); }

        <MATHINLINE_STATE>"%{"{placeholder}"}%"        { returntoken(MATHBLOCK_VERBATIM_PLACEHOLDER); }
        "%{"{placeholder}"}%"                   { returntoken(PLACEHOLDER); }
        "\\"{word}(\.{word})*                              { returntoken(LATEX_COMMAND); }
        "\\"{word}(\.{word})*"{}"?"["{whitespace_nl}       { returntoken(LATEX_COMMAND_WITH_ARGUMENTS); }
        "\\"{word}(\.{word})*"{"{whitespace_nl}            { STATE_PUSH(ATTRIBUTE_STATE); returntoken(LATEX_COMMAND_WITH_OPTIONAL_ARGUMENT); }

        {whitespace}"|"{whitespace}             { returntoken(TABLE_DELIM); }
        {whitespace}[-+]{3,}{whitespace}        { returntoken(TABLE_HRULE); }
        {whitespace}:---+{whitespace}           { returntoken(TABLE_HRULE_LEFT_ALIGNED); }
        {whitespace}:---+:{whitespace}          { returntoken(TABLE_HRULE_CENTERED); }
        {whitespace}---+:{whitespace}           { returntoken(TABLE_HRULE_RIGHT_ALIGNED); }

        <INITIAL>{whitespace}```                { STATE_PUSH(CODEBLOCK_STATE); returntoken(CODEBLOCK_START); }
        <CODEBLOCK_STATE>{whitespace}"{"        { STATE_PUSH(ATTRIBUTE_STATE); returntoken(ATTR_START); }
        <CODEBLOCK_STATE>{whitespace}\n         { STATE_PUSH(CODEBLOCK_STATE_VERBATIM); returntoken(CODEBLOCK_BR); }
        <CODEBLOCK_STATE>[^ {\n]+               { returntoken(CODEBLOCK_STRING_BEFORE); }
        <CODEBLOCK_STATE_VERBATIM>\n            { returntokenFromString(yytext,CODEBLOCK_CHAR); }
        <CODEBLOCK_STATE_VERBATIM>{whitespace}```{whitespace}  { STATE_POP(); STATE_POP(); returntoken(CODEBLOCK_END); }
        <CODEBLOCK_STATE_VERBATIM>{any}         { returntokenFromString(yytext,CODEBLOCK_CHAR); }

        <INITIAL>"`"                            { STATE_PUSH(CODEINLINE_STATE); returntoken(CODEINLINE_START); }
        <CODEINLINE_STATE>\n                    { returntokenFromString(yytext,CODEINLINE_CHAR); }
        <CODEINLINE_STATE>"\`"                  { STATE_POP(); returntoken(CODEINLINE_END); }
        <CODEINLINE_STATE>\n"\`"                { STATE_POP(); returntoken(CODEINLINE_END); }
        <CODEINLINE_STATE>"\\\`"                { returntokenFromString(yytext,CODEINLINE_CHAR); }
        <CODEINLINE_STATE>{any}                 { returntokenFromString(yytext,CODEINLINE_CHAR); }

        <INITIAL>"\$\$"                         { STATE_PUSH(MATHINLINE_STATE); returntoken(MATHBLOCK_START); }
        <INITIAL>"\$"                           { STATE_PUSH(MATHINLINE_STATE); returntoken(MATHINLINE_START); }
            <MATHINLINE_STATE>"\\{"             { returntokenFromString(chr_bs_curly_open, MATHBLOCK_CHAR); }
            <MATHINLINE_STATE>"\\}"             { returntokenFromString(chr_bs_curly_close, MATHBLOCK_CHAR); }
            <MATHINLINE_STATE>"\\\$"            { returntokenFromString(chr_dollar, MATHBLOCK_CHAR); }
            <MATHINLINE_STATE>"\\\\"            { returntokenFromString(chr_bs_backslash, MATHBLOCK_CHAR); }
            <MATHINLINE_STATE>"\\"{word}(\.{word})*        { returntoken(MATHBLOCK_LATEX_COMMAND); }
            <MATHINLINE_STATE>"{"               { returntoken(MATHBLOCK_CURLY_OPEN); }
            <MATHINLINE_STATE>"}"               { returntoken(MATHBLOCK_CURLY_CLOSE); }
        <MATHINLINE_STATE>{word}                { returntokenFromString(yytext, MATHBLOCK_CHAR); }
        <MATHINLINE_STATE>\n                    { returntokenFromString(yytext, MATHBLOCK_CHAR); }
        <MATHINLINE_STATE>"\$\$"|"\$"           { STATE_POP(); returntoken(MATH_END); }
        <MATHINLINE_STATE>{any}                 { returntokenFromString(yytext, MATHBLOCK_CHAR); }

        <INITIAL>^{whitespace}"{"               { STATE_PUSH(ATTRIBUTE_STATE); returntoken(ATTR_START); }
        <INITIAL>"{"                            { STATE_PUSH(ATTRIBUTE_STATE); returntoken(ATTR_START); }
        <ATTRIBUTE_STATE>"{"                    { STATE_PUSH(ATTRIBUTE_STATE); returntoken(ATTR_START); }
        <ATTRIBUTE_STATE>{whitespace_nl}"}"{whitespace}        { STATE_POP(); returntoken(ATTR_END); }
        <ATTRIBUTE_STATE>"}["                   { STATE_POP(); returntoken(ATTR_END_AND_ARG_START); }
        <ATTRIBUTE_STATE>"["                    { STATE_PUSH(INITIAL); returntoken(ATTR_INPUT); }
        <ATTRIBUTE_STATE>"#"                    { returntoken(ATTR_HASH); }
        <ATTRIBUTE_STATE>"\."                   { returntoken(ATTR_DOT); }
        <ATTRIBUTE_STATE>"!"                    { returntoken(ATTR_EXCLAMATION); }
        <ATTRIBUTE_STATE>{whitespace_nl}"="{whitespace_nl}                    { returntoken(ATTR_EQUAL); }
        <ATTRIBUTE_STATE>{whitespace_nl}":"{whitespace_nl}                    { returntoken(ATTR_EQUAL); }
        <ATTRIBUTE_STATE>{whitespace_nl}","{whitespace_nl}                    { returntoken(ATTR_COMMA); }
        <ATTRIBUTE_STATE>[ \n\t]+               { returntoken(ATTR_COMMA); }
        <ATTRIBUTE_STATE>[Tt]"rue"?             { returntoken(ATTR_BOOLEAN); }
        <ATTRIBUTE_STATE>[Ff]"alse"?            { returntoken(ATTR_BOOLEAN); }
        <ATTRIBUTE_STATE>[0-9]+([\.,][0-9]+)?   { returntoken(ATTR_NUMBER); }
        <ATTRIBUTE_STATE>"'"[^\']*"'"           { returntoken(ATTR_STRING); }
        <ATTRIBUTE_STATE>"\""[^\"]*"\""         { returntoken(ATTR_STRING); }
        <ATTRIBUTE_STATE>"%{"{placeholder}"}%"  { returntoken(ATTR_PLACEHOLDER); }
        <ATTRIBUTE_STATE>"\$\$"                 { STATE_PUSH(MATHINLINE_STATE); returntoken(MATHBLOCK_START); }
        <ATTRIBUTE_STATE>"\$"                   { STATE_PUSH(MATHINLINE_STATE); returntoken(MATHINLINE_START); }
        <ATTRIBUTE_STATE>{word}                 { returntoken(ATTR_WORD); }
        <ATTRIBUTE_STATE>{any}                  { }


        ^{whitespace}"[^"[^\]]+"]:"{whitespace} { returntoken(FOOTNOTE_DEFINITION); }
        ^{whitespace}"^["[^\]]+"]:"{whitespace} { returntoken(FOOTNOTE_DEFINITION); }
        ^{whitespace}"!["[^\]]+"]:"{whitespace} { returntoken(IMAGE_DEFINITION); }
        ^{whitespace}"["[^\^\]]+"]:"{whitespace} { returntoken(LINK_DEFINITION); }
        "[^"                                    { returntoken(FOOTNOTE_START); }
        "][^"                                   { returntoken(FOOTNOTE_MID); }
        "^["                                    { returntoken(FOOTNOTE_INLINE_START); }
        "]^["                                   { returntoken(FOOTNOTE_INLINE_MID); }
        "!["                                    { returntoken(IMG_START); }
        "["                                     { returntoken(LINK_START); }
        "]["{whitespace_nl}                     { returntoken(HYPERREF_REF_MID); }
        "]("{whitespace_nl}"```"\w*{whitespace_nl}    {  STATE_PUSH(HYPERREF_CODE_STATE); returntoken(HYPERREF_CODE_START); }
        "]("{whitespace_nl}                     { STATE_PUSH(HYPERREF_LINK_STATE); returntoken(HYPERREF_LINK_MID); }
        "]"                                     { STATE_POP(); returntoken(HYPERREF_REF_END); }

        <HYPERREF_LINK_STATE>{whitespace_nl}")" { STATE_POP(); returntoken(HYPERREF_LINK_END); }
        <HYPERREF_LINK_STATE>{whitespace_nl}\"  { STATE_POP(); STATE_PUSH(HYPERREF_LINK_ALT_STATE); returntoken(HYPERREF_LINK_ALT_START); }
        <HYPERREF_LINK_STATE>{any}              { returntokenFromString(yytext,HYPERREF_LINK_CHAR); }
        <HYPERREF_LINK_STATE>{whitespace_nl}    { returntokenFromString(yytext,HYPERREF_LINK_CHAR); }
        <HYPERREF_LINK_ALT_STATE>{any}          { returntokenFromString(yytext,HYPERREF_LINK_ALT_CHAR); }
        <HYPERREF_LINK_ALT_STATE>{whitespace_nl}          { returntokenFromString(yytext,HYPERREF_LINK_ALT_CHAR); }
        <HYPERREF_LINK_ALT_STATE>\"{whitespace_nl}")"       { STATE_POP(); returntoken(HYPERREF_LINK_ALT_END); }

        <HYPERREF_CODE_STATE>\n                 { returntokenFromString(yytext,HYPERREF_CODE_CHAR); }
        <HYPERREF_CODE_STATE>"```"{whitespace_nl}")"                { STATE_POP(); returntoken(HYPERREF_CODE_END); }
        <HYPERREF_CODE_STATE>{any}              { returntokenFromString(yytext,HYPERREF_CODE_CHAR); }



        ^\n\_\_\_+/\n                           { returntoken(HRULE); }
        ^\n---+/\n                              { returntoken(HRULE); }
        ^\n\*\*\*+/\n                           { returntoken(HRULE); }

        ^{whitespace}#/[^#]                     { returntoken(HEADINGHASH_END); }
        ^{whitespace}#                          { STATE_PUSH(HEADINGHASH_STATE); returntoken(HEADINGHASH); }
        <HEADINGHASH_STATE>#/[^#]               { STATE_POP(); returntoken(HEADINGHASH_END); }
        <HEADINGHASH_STATE>#                    { returntoken(HEADINGHASH); }
        \n{indent}*===+/\n                      { returntoken(HEADING_ULINEDBL); }
        \n{indent}*---+/\n                      { returntoken(HEADING_ULINESGL); }
        ^{indent}*[\*\-\+]" "{whitespace}       { returntoken(ULIST_SYM); }
        ^{indent}*[\*\-\+]\[[a-zA-Z\-\_\?]+\]" "{whitespace}        { returntoken(ULIST_SYM); }
        ^{indent}*[\*\-\+]\[{whitespace}*\]" "{whitespace}        { returntoken(ULIST_SYM); }
        ^{indent}*[\*\-\+]\[{utf_8}\]" "{whitespace}        { returntoken(ULIST_SYM); }
        ^{indent}*[ivxlcdmlIVXLCDML0-9]+". "{whitespace}          { returntoken(OLIST_SYM); }
        ^{indent}*[a-zA-Z]". "{whitespace}      { returntoken(OLIST_SYM); }
        ^{indent}*"> "{whitespace}              { returntoken(QUOTE_SYM); }
        ^{indent}+                              { returntoken(INDENT_SYM); }

        "**"                                    { ess_state_stack('s',STRONG_START,STRONG_END) }
        "*"                                     { ess_state_stack('e',EMPH_START,EMPH_END) }
        "__"                                    { ess_state_stack('b',BOLD_START,BOLD_END) }
        "_"                                     { ess_state_stack('i',ITALIC_START,ITALIC_END) }
        "~~"                                    { ess_state_stack('-',STRIKE_START,STRIKE_END) }

        \n                                      { returntoken(BR); }
        " "+                                    { returntokenFromString(chr_space, CHAR); }
        [a-zA-Z0-9„“-—',.:;()]+                 { returntokenFromString(yytext, CHAR); }
        {any}                                   { returntokenFromString(yytext, CHAR); }
        <<EOF>> {
                while (ais_i!= -1) {
                    int end_would_be_unexpected = 1;
                    if (ais[ais_i] == ML_COMMENT || ais[ais_i] == COMMENT)
                        end_would_be_unexpected = 0;
                    STATE_POP();
                    //printf("Current State -> index:%d state:%d\n",ais_i,ais[ais_i]);
                    if (end_would_be_unexpected) {
                        yyset_extra(1,yyscanner);
                        reset_stacks();
                        returntoken(UNEXPECTED_END);
                    }
                }

                // reset stacks
                reset_stacks();

                yyterminate();
            }

        %%

        int yywrap(yyscan_t scanner) {
          /* we will just terminate when we reach the end of the input file */
          return 1;
        }

        """


        def make_string_rule(prefix="", allowempty=False):
            if prefix != "":
                prefix = prefix + "_"
            emptyrule = "" if not allowempty else """
                | {{
                    char * new_str ;
                    if((new_str = malloc(1)) != NULL) {{
                        new_str[0] = '\\0';
                    }}
                    $$ = new_str;
                  }}
            """

            return """
            {prefix}string : {prefix}string2 {{ $$ = PyUnicode_FromString(strdup($1)); }};
            {prefix}string2 : {PREFIX}CHAR {{ $$ = $1; }}
                    | {prefix}string2 {PREFIX}CHAR {{
                        char * new_str ;
                        if((new_str = malloc(strlen($1)+strlen($2)+1)) != NULL) {{
                            new_str[0] = '\\0';   // ensures the memory is an empty string
                            strcpy(new_str,$1);
                            strcat(new_str,$2);
                        }}
                        $$ = new_str;
                    }};
                    {emptyrule}


            """.format(prefix=prefix, PREFIX=prefix.upper(), emptyrule=emptyrule)



        self.raw_c_rules = "\n\n\n".join([
            make_string_rule(),
            make_string_rule("mathblock",False),
            make_string_rule("hyperref_code",True),
            make_string_rule("codeinline", True),
            make_string_rule("hyperref_link",True),
            make_string_rule("hyperref_link_alt",True),
            make_string_rule("codeblock",True)
        ])

        self.handlesErrorRules = True


        buildDirectory = os.path.join(os.path.dirname(__file__),"compiled")+os.path.sep
        super(MarkdownParser, self).__init__(buildDirectory=buildDirectory,**kwargs)

    # ---------------------------------------------------------------
    # These methods are the python handlers for the bison targets.
    # (which get called by the bison code each time the corresponding
    # parse target is unambiguously reached)
    #
    # WARNING - don't touch the method docstrings unless you know what
    # you are doing - they are in bison rule syntax, and are passed
    # verbatim to bison to build the parser engine library.
    # ---------------------------------------------------------------

    # ---------------- #
    # helper functions #
    # ---------------- #

    @staticmethod
    def dictupdate(old, new):
        old.update(new)
        return old

    @staticmethod
    def parseUrl(url):
        if url.startswith("%{") and url.endswith("}%"):
            return {'type': 'placeholder', 'command': url[2:-2]}
        return url

    @staticmethod
    def attribute_args(val):
        v = {"nargs": []}
        for v2 in val:
            if isinstance(v2, dict) and (not "type" in v2 or v2["type"] != "placeholder") and not isinstance(v2, attr_dict):
                if "classes" in v2:
                    if "classes" not in v:
                        v["classes"] = []
                    v["classes"].append(v2["classes"])
                else:
                    v.update(v2)
            else:
                v["nargs"].append(v2)
        return v

    @staticmethod
    def ulist_sym_get(s):
        s = s.strip()
        if len(s) >= 2 and s[1] == "[":
            s = s[2:-1]
        return s

    def on_input_start(self, target, option, names, values):
        """
        input_start : input
        """
        self.last_list += values[0]
        return self.last_list

    def on_input(self, target, option, names, values):
        """
        input : blocks
              | blocks br_end
              | br blocks br_end
              | br blocks
              | br_end
              |
        """
        if option <= 1:
            return values[0]
        elif option == 4 or option == 5:
            return []
        else:
            return values[1]

    def on_blocks(self, target, option, names, values):
        """
        blocks : block
               | blocks br block
        """
        if option == 0:
            return [values[0]]
        elif option == 1:
            if values[1] == "hard":
                return values[0] + [{'type': 'hard break'}, values[2]]
            elif values[1] == "newline":
                return values[0] + [{'type': 'new line'}, values[2]]
            return values[0] + [values[2]]

    def on_block(self, target, option, names, values):
        """
        block : header
              | text
              | ulist
              | olist
              | quote
              | indent
              | HRULE
              | attributes
              | table
              | codeblock_block
              | href_definition
              | error
        """
        if option == 1:
            return {'type': 'paragraph', 'content': MLList([values[0]])}
        elif option == 6:
            return {'type': 'hrule'}
        elif option == 7:
            return {'type': 'attributes', **values[0]}
        elif option == 11:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in %s-Element" % (target)),"exception-type":"Syntax Error","text":values[0][0],"pos":values[0][1:]}
        return values[0]

    def on_br(self, target, option, names, values):
        """
        br : BR
           | NEWLINE
           | br BR
           | br INDENT_SYM BR
        """
        if option == 0:
            return 'soft'
        elif option == 1:
            return 'newline'
        else:
            return 'hard'

    def on_br_end(self, target, option, names, values):
        """
        br_end : br
               | br INDENT_SYM
        """
        return values[0]

    def on_indent(self, target, option, names, values):
        """
        indent : INDENT_SYM text
        """
        return {'type': 'indent', 'content': [values[1]], 'level': values[0]}

    def on_quote(self, target, option, names, values):
        """
        quote : QUOTE_SYM text attributes
              | QUOTE_SYM attributes
              | QUOTE_SYM text
              | QUOTE_SYM
        """
        if option == 0:
            return {'type': 'quote', 'content': [values[1]], 'level': values[0], **values[2]}
        elif option == 1:
            return {'type': 'quote', 'content': [], 'level': values[0], **values[1]}
        elif option == 2:
            return {'type': 'quote', 'content': [values[1]], 'level': values[0]}
        elif option == 3:
            return {'type': 'quote', 'content': [], 'level': values[0]}

    def on_ulist(self, target, option, names, values):
        """
        ulist : ULIST_SYM text attributes
              | ULIST_SYM attributes
              | ULIST_SYM text
              | ULIST_SYM
        """
        if option == 0:
            return {'type': 'ulist', 'content': [values[1]], 'level': values[0], **values[2], 'symbols': [MarkdownParser.ulist_sym_get(values[0])]}
        elif option == 1:
            return {'type': 'ulist', 'content': [], 'level': values[0], **values[1], 'symbols': [MarkdownParser.ulist_sym_get(values[0])]}
        elif option == 2:
            return {'type': 'ulist', 'content': [values[1]], 'level': values[0], 'symbols': [MarkdownParser.ulist_sym_get(values[0])]}
        elif option == 3:
            return {'type': 'ulist', 'content': [], 'level': values[0], 'symbols': [MarkdownParser.ulist_sym_get(values[0])]}

    def on_olist(self, target, option, names, values):
        """
        olist : OLIST_SYM text attributes
              | OLIST_SYM attributes
              | OLIST_SYM text
              | OLIST_SYM
        """
        if option == 0:
            return {'type': 'olist', 'content': [values[1]], 'level': values[0], 'symbols': [values[0].strip()], **values[2]}
        elif option == 1:
            return {'type': 'olist', 'content': [], 'level': values[0], 'symbols': [values[0].strip()], **values[1]}
        elif option == 2:
            return {'type': 'olist', 'content': [values[1]], 'level': values[0], 'symbols': [values[0].strip()]}
        elif option == 3:
            return {'type': 'olist', 'content': [], 'level': values[0], 'symbols': [values[0].strip()]}

    def on_href_definition(self, target, option, names, values):
        """
        href_definition : IMAGE_DEFINITION URL
                        | LINK_DEFINITION URL
                        | IMAGE_DEFINITION URL text
                        | LINK_DEFINITION URL text
                        | FOOTNOTE_DEFINITION text
                        | FOOTNOTE_DEFINITION
        """
        if option == 0:
            return {'type': 'image_definition', 'ref': values[0].strip()[2:-2].lower(), 'dest': MarkdownParser.parseUrl(values[1]), 'content': MLList(), 'level': ""}
        elif option == 1:
            return {'type': 'link_definition', 'ref': values[0].strip()[1:-2].lower(), 'dest': MarkdownParser.parseUrl(values[1]), 'content': MLList(), 'level': ""}
        elif option == 2:
            if len(values[2]) > 0 and isinstance(values[2][0], str):
                values[2][0] = values[2][0].lstrip()
                values[2][0] = values[2][0].lstrip("\"'")
            if len(values[2]) > 0 and isinstance(values[2][-1], str):
                values[2][-1] = values[2][-1].rstrip()
                values[2][-1] = values[2][-1].rstrip("'\"")
            return {'type': 'image_definition', 'ref': values[0].strip()[2:-2].lower(), 'dest': MarkdownParser.parseUrl(values[1]), 'content':MLList(values[2]), 'level': ""}
        elif option == 3:
            if len(values[2]) > 0 and isinstance(values[2][0], str):
                values[2][0] = values[2][0].lstrip()
                values[2][0] = values[2][0].lstrip("\"'")
            if len(values[2]) > 0 and isinstance(values[2][-1], str):
                values[2][-1] = values[2][-1].rstrip()
                values[2][-1] = values[2][-1].rstrip("'\"")
            return {'type': 'link_definition', 'ref': values[0].strip()[1:-2].lower(), 'dest': MarkdownParser.parseUrl(values[1]), 'content':MLList(values[2]), 'level': ""}
        elif option == 4:
            return {'type': 'footnote_definition', 'ref': values[0].strip()[2:-2].lower(), 'content': MLList(values[1]), "level": ""}
        elif option == 5:
            return {'type': 'footnote_definition', 'ref': values[0].strip()[2:-2].lower(), 'content': MLList(), "level": ""}

    def on_header(self, target, option, names, values):
        """
        header : header_hash
               | text attributes HEADING_ULINEDBL
               | text attributes HEADING_ULINESGL
               | text HEADING_ULINEDBL
               | text HEADING_ULINESGL
        """
        if option == 0:
            values[0]['level'] = values[0]['level']
            return values[0]
        elif option == 1:
            return {'type': 'section', **MarkdownParser.dictupdate({'title': values[0], 'h-level': 0, 'level': values[2][1:]}, values[1])}
        elif option == 2:
            return {'type': 'section', **MarkdownParser.dictupdate({'title': values[0], 'h-level': 1, 'level': values[2][1:]}, values[1])}
        elif option == 3:
            return {'type': 'section', 'title': values[0], 'h-level': 0, 'level': values[1][1:]}
        elif option == 4:
            return {'type': 'section', 'title': values[0], 'h-level': 1, 'level': values[1][1:]}

    def on_header_hash(self, target, option, names, values):
        """
        header_hash : HEADINGHASH_END text attributes
                    | HEADINGHASH_END text
                    | HEADINGHASH header_hash
        """
        if option == 0:
            return {'type': 'section', **MarkdownParser.dictupdate({'title': values[1], 'h-level': 0, 'level': values[0]}, values[2])}
        if option == 1:
            return {'type': 'section', 'title': values[1], 'h-level': 0, 'level': values[0]}
        elif option == 2:
            values[1]['h-level'] += 1
            values[1]['level'] = values[0]
            return values[1]

    def on_text(self, target, option, names, values):
        """
        text : span
             | attributes span
             | text span
             | text attributes span
        """
        if option == 0:
            return [values[0]]
        elif option == 1:
            values[1].update(values[0])
            return [values[1]]
        elif option == 2:
            return values[0] + [values[1]]
        elif option == 3:
            if isinstance(values[2],dict):
                values[2].update(values[1])
            return values[0] + [values[2]]

    def on_span(self, target, option, names, values):
        """
        span : string
             | EMPH_START span_multitext_wrap EMPH_END
             | STRONG_START span_multitext_wrap STRONG_END
             | ITALIC_START span_multitext_wrap ITALIC_END
             | BOLD_START span_multitext_wrap BOLD_END
             | STRIKE_START span_multitext_wrap STRIKE_END
             | math
             | CODEINLINE_START codeinline_string CODEINLINE_END
             | hyperref
             | latex
             | PLACEHOLDER
             | EMPH_START span_multitext_wrap
             | STRONG_START span_multitext_wrap
             | ITALIC_START span_multitext_wrap
             | BOLD_START span_multitext_wrap
             | STRIKE_START span_multitext_wrap
             | error UNEXPECTED_END
        """
        # raise ValueError("test")
        if option == 0:
            return values[0]
        elif option == 1 or option == 11:
            return {'type': 'emph', 'text': values[1]}
        elif option == 2 or option == 12:
            return {'type': 'strong', 'text': values[1]}
        elif option == 3 or option == 13:
            return {'type': 'italic', 'text': values[1]}
        elif option == 4 or option == 14:
            return {'type': 'bold', 'text': values[1]}
        elif option == 5 or option == 15:
            return {'type': 'strike', 'text': values[1]}
        elif option == 7:
            return {'type': 'code_inline', 'verbatim': values[1].replace("\\`","`")}
        elif option == 10:
            return {'type': 'placeholder', 'command': values[0][2:-2]}
        elif option == 16:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in Block-Element"),"exception-type":"Syntax Error","text":values[0][0],"pos":values[0][1:]}
        return values[0]

    def on_span_multitext_wrap(self, target, option, names, values):
        """
        span_multitext_wrap : span_multitext
                            | br span_multitext
        """
        if option == 1:
            return values[1]
        return values[0]

    def on_span_multitext(self, target, option, names, values):
        """
        span_multitext : text
                       | text br span_multitext
                       |
        """
        if option == 0:
            return values[0]
        elif option == 1:
            if values[1] == "hard":
                return values[0] + [{'type': 'hard break'}, values[2]]
            elif values[1] == "newline":
                return values[0] + [{'type': 'new line'}, values[2]]
            else:
                return values[0] + [values[2]]
        elif option == 2:
            return ""

    # def on_string(self, target, option, names, values):
    #     """
    #     string : CHAR
    #            | string CHAR
    #     """
    #     if option == 0:
    #         return values[0]
    #     elif option == 1:
    #         return values[0] + values[1]

    # ===== #
    # latex #
    # ===== #

    def on_latex(self, target, option, names, values):
        """
        latex : LATEX_COMMAND
              | latex_command_with_arguments input HYPERREF_REF_END
              | LATEX_COMMAND_WITH_OPTIONAL_ARGUMENT attribute_list ATTR_END
              | latex_command_with_arguments_and_optional input HYPERREF_REF_END
              | latex_command_with_arguments error
              | latex_command_with_arguments_and_optional error
        """
        if option == 0:
            cmd = {'type': 'command', 'command': values[0][1:].rstrip("[\t\n "), 'arguments': []}
        elif option == 1:
            cmd = {'type': 'command', 'command': values[0]["command"], 'arguments': values[0]["arguments"] + MLList([values[1]])}
        elif option == 2:
            cmd = {'type': 'command', 'command': values[0][1:].rstrip("[\t\n ")[:-1].rstrip("[\t\n "), **MarkdownParser.attribute_args(values[1])}
        elif option == 3:
            values[0]['arguments'] += MLList([values[1]])
            cmd = values[0]
        elif option == 4 or option == 5:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in Block-Element"),"exception-type":"Syntax Error","text":"Unexpected End","text":values[1][0],"pos":values[1][1:]}

        return cmd

    def on_latex_command_with_arguments_and_optional(self, target, option, names, values):
        """
        latex_command_with_arguments_and_optional : LATEX_COMMAND_WITH_OPTIONAL_ARGUMENT attribute_list ATTR_END_AND_ARG_START
                                                  | latex_command_with_arguments_and_optional input HYPERREF_REF_MID
                                                  | latex_command_with_arguments_and_optional error
        """
        if option == 0:
            return {'type': 'command', 'command': values[0][1:].rstrip("[\t\n ")[:-1].rstrip("[\t\n "), 'arguments': [], **MarkdownParser.attribute_args(values[1])}
        elif option == 1:
            values[0]['arguments'] += MLList([values[1]])
            return values[0]
        elif option == 2:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in Block-Element"),"exception-type":"Syntax Error","text":"Unexpected End","text":values[1][0],"pos":values[1][1:]}

    def on_latex_command_with_arguments(self, target, option, names, values):
        """
        latex_command_with_arguments : LATEX_COMMAND_WITH_ARGUMENTS
                                     | latex_command_with_arguments input HYPERREF_REF_MID
                                     | latex_command_with_arguments error
        """
        if option == 0:
            return {'type': 'command', 'command': values[0][1:].replace("{}", "").rstrip("[\t\n "), 'arguments': []}
        elif option == 1:
            return {'type': 'command', 'command': values[0]["command"], 'arguments': values[0]["arguments"] + MLList([values[1]])}
        elif option == 2:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in Block-Element"),"exception-type":"Syntax Error","text":"Unexpected End","text":values[1][0],"pos":values[1][1:]}

    # ===== #
    # table #
    # ===== #

    def on_table(self, target, option, names, values):
        """
        table : table_delim
              | table_no_delim
              | table_delim_separator
              | table_no_delim_separator
              | INDENT_SYM table
        """
        if option == 2 or option == 3:
            return {'type': 'table', 'content': [values[0]]}
        elif option == 4:
            return {**values[1], 'level': values[0]}
        return {'type': 'table', 'content': [values[0]]}

    def on_table_delim(self, target, option, names, values):
        """
        table_delim : TABLE_DELIM text TABLE_DELIM
                    | table_delim text TABLE_DELIM
                    | TABLE_DELIM TABLE_DELIM
                    | table_delim TABLE_DELIM
        """
        if option == 0:
            return [values[1]]
        elif option == 1:
            return values[0] + [values[1]]
        elif option == 2:
            return [[]]
        elif option == 3:
            return values[0] + [[]]

    def on_table_no_delim(self, target, option, names, values):
        """
        table_no_delim : text TABLE_DELIM text
                       | table_no_delim TABLE_DELIM text
        """
        if option == 0:
            return [values[0], values[2]]
        return values[0] + [values[2]]

    def on_table_delim_separator(self, target, option, names, values):
        """
        table_delim_separator : TABLE_DELIM table_alignment TABLE_DELIM
                              | table_delim_separator table_alignment TABLE_DELIM
        """
        if option == 0:
            return [values[1]]
        return values[0] + [values[1]]

    def on_table_no_delim_separator(self, target, option, names, values):
        """
        table_no_delim_separator : table_alignment TABLE_DELIM table_alignment
                                 | table_no_delim_separator TABLE_DELIM table_alignment
        """
        if option == 0:
            return [values[0], values[2]]
        return values[0] + [values[2]]

    def on_table_alignment(self, target, option, names, values):
        """
        table_alignment : TABLE_HRULE
                        | TABLE_HRULE_CENTERED
                        | TABLE_HRULE_LEFT_ALIGNED
                        | TABLE_HRULE_RIGHT_ALIGNED
                        | attributes table_alignment
        """
        if option == 0:
            return {'type': 'table_separator', 'align': "normal"}
        elif option == 1:
            return {'type': 'table_separator', 'align': "centered"}
        elif option == 2:
            return {'type': 'table_separator', 'align': "left"}
        elif option == 3:
            return {'type': 'table_separator', 'align': "right"}
        elif option == 4:
            return MarkdownParser.dictupdate(values[1], values[0])

    # ============== #
    # HYPERREF STATE #
    # ============== #

    def on_hyperref(self, target, option, names, values):
        """
        hyperref : hyperref_start input HYPERREF_LINK_MID hyperref_link_string HYPERREF_LINK_END
                 | hyperref_start input HYPERREF_LINK_MID hyperref_link_string HYPERREF_LINK_ALT_START hyperref_link_alt_string HYPERREF_LINK_ALT_END
                 | hyperref_start input HYPERREF_REF_MID string HYPERREF_REF_END
                 | hyperref_start string HYPERREF_REF_END
                 | URL
                 | FOOTNOTE_START string HYPERREF_REF_END
                 | FOOTNOTE_INLINE_START input HYPERREF_REF_END
                 | hyperref_start input FOOTNOTE_MID string HYPERREF_REF_END
                 | hyperref_start input FOOTNOTE_INLINE_MID input HYPERREF_REF_END
                 | hyperref_start input HYPERREF_CODE_START hyperref_code_string HYPERREF_CODE_END
                 | hyperref_start error
                 | FOOTNOTE_INLINE_START error
        """
        if option == 0:
            return {'type': values[0], 'content': MLList(values[1]), 'dest': MarkdownParser.parseUrl(values[3])}
        elif option == 1:
            return {'type': values[0], 'alt_text': values[5], 'dest': MarkdownParser.parseUrl(values[3]), 'content': MLList(values[1])}
        elif option == 2:
            return {'type': values[0], 'content': MLList(values[1]), 'ref': values[3].lower()}
        elif option == 3:
            return {'type': values[0], 'content': MLList([values[1].lower()]), 'ref': values[1].lower()}
        elif option == 4:
            url = values[0]
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]
            return {'type': 'url', 'dest': MarkdownParser.parseUrl(url)}
        elif option == 5:
            return {'type': 'footnote', 'ref': values[1].lower(), 'text': ''}
        elif option == 6:
            return {'type': 'footnote_inline', 'content': MLList([values[1]]), 'text': ''}
        elif option == 7:
            return {'type': 'footnote' if values[0] == 'link' else 'note', 'ref': values[3].lower(), 'text': MLList([values[1]])}
        elif option == 8:
            return {'type': 'footnote_inline' if values[0] == 'link' else 'note_inline', 'content': MLList(values[3]), 'text': MLList(values[1])}
        elif option == 9:
            return {'type': 'tikz', 'content': MLList(values[1]), 'tikz-code': values[3].strip()}
        elif option == 10 or option == 11:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in Block-Element"),"exception-type":"Syntax Error","text":"Unexpected End","text":values[1][0],"pos":values[1][1:]}

    def on_hyperref_start(self, target, option, names, values):
        """
        hyperref_start : LINK_START
                       | IMG_START
        """
        if option == 0:
            return 'link'
        elif option == 1:
            return 'image'

    # ========== #
    # MATH STATE #
    # ========== #

    def on_math(self, target, option, names, values):
        """
        math  : MATHBLOCK_START mathblock_text MATH_END
              | MATHINLINE_START mathblock_text MATH_END
        """
        if option == 0:
            return {'type': 'math_block', 'verbatim': values[1]}
        else: # option == 1:
            return {'type': 'math_inline', 'verbatim': values[1]}

    def on_mathblock_text(self, target, option, names, values):
        """
        mathblock_text : mathblock_span
                       | mathblock_span mathblock_text
                       | MATHBLOCK_CURLY_OPEN mathblock_text MATHBLOCK_CURLY_CLOSE
                       | MATHBLOCK_CURLY_OPEN mathblock_text MATHBLOCK_CURLY_CLOSE mathblock_text
        """
        if option == 0:
            return [values[0]]
        elif option == 1:
            return [values[0]] + values[1]
        elif option == 2:
            return [values[0]] + values[1] + [values[2]]
        elif option == 3:
            return [values[0]] + values[1] + [values[2]] + values[3]

    def on_mathblock_span(self, target, option, names, values):
        """
        mathblock_span : mathblock_string
                       | mathblock_latex
                       | MATHBLOCK_VERBATIM_PLACEHOLDER
                       | MATHBLOCK_CURLY_OPEN MATHBLOCK_CURLY_CLOSE
        """
        if option == 2:
            return {'type': 'placeholder', 'command': values[0][2:-2]}
        elif option == 3:
            return values[0] + values[1]
        return values[0]

    # def on_mathblock_string(self, target, option, names, values):
    #     """
    #     mathblock_string : MATHBLOCK_CHAR
    #                      | mathblock_string MATHBLOCK_CHAR
    #     """
    #     if option == 0:
    #         return values[0]
    #     else:
    #         return values[0] + values[1]

    def on_mathblock_latex(self, target, option, names, values):
        """
        mathblock_latex : MATHBLOCK_LATEX_COMMAND
                        | mathblock_latex MATHBLOCK_CURLY_OPEN mathblock_text MATHBLOCK_CURLY_CLOSE
        """
        if option == 0:
            return {'type': 'latex_command', 'command': values[0][1:], 'arguments': []}
        elif option == 1:
            return {'type': 'latex_command', 'command': values[0]["command"], 'arguments': values[0]["arguments"] + [values[2]]}

    # =============== #
    # CODEBLOCK STATE #
    # =============== #

    def on_codeblock_block(self, target, option, names, values):
        """
        codeblock_block : CODEBLOCK_START CODEBLOCK_STRING_BEFORE attributes CODEBLOCK_BR codeblock_string CODEBLOCK_END
                        | CODEBLOCK_START CODEBLOCK_STRING_BEFORE CODEBLOCK_BR codeblock_string CODEBLOCK_END
                        | CODEBLOCK_START attributes CODEBLOCK_BR codeblock_string CODEBLOCK_END
                        | CODEBLOCK_START CODEBLOCK_BR codeblock_string CODEBLOCK_END
                        | codeblock_block error
        """
        if option == 0:
            return {'type': 'code_block', 'syntax': values[1], 'verbatim': values[4].replace("\\`","`"), 'whitespace': values[0][:-3], 'level': values[0], **values[2]}
        elif option == 1:
            return {'type': 'code_block', 'syntax': values[1], 'verbatim': values[3].replace("\\`","`"), 'whitespace': values[0][:-3], 'level': values[0]}
        elif option == 2:
            return {'type': 'code_block', 'verbatim': values[3].replace("\\`","`"), 'whitespace': values[0][:-3], 'level': values[0], **values[1]}
        elif option == 3:
            return {'type': 'code_block', 'verbatim': values[2].replace("\\`","`"), 'whitespace': values[0][:-3], 'level': values[0]}
        elif option == 4:
            return {"type":"error","exception-object":BisonSyntaxError("Error Occured in %s-Element" % (target)),"exception-type":"Syntax Error","text":"Codeblock is a block-element and has to end with a NEWLINE-Symbol","pos":values[-1][1:]}

    # ================ #
    # ATTRIBUTES STATE #
    # ================ #

    @staticmethod
    def num(s):
        s = str(s).replace(',', '.')
        try:
            return int(s)
        except ValueError:
            return float(s)

    @staticmethod
    def bool(s):
        if s[0] == "T" or s[0] == "t":
            return True
        else:
            return False

    def on_attributes(self, target, option, names, values):
        """
        attributes : ATTR_START attribute_list ATTR_END
        """
        return MarkdownParser.attribute_args(values[1])

    def on_attribute_list(self, target, option, names, values):
        """
        attribute_list : attribute
                       | attribute_list attribute
                       | attribute_list ATTR_COMMA attribute
                       |
        """
        if option == 0:
            return [values[0]]
        elif option == 1:
            return values[0] + [values[1]]
        elif option == 2:
            return values[0] + [values[2]]
        elif option == 3:
            return []

    def on_attribute(self, target, option, names, values):
        """
        attribute : ATTR_HASH ATTR_WORD
                  | ATTR_DOT ATTR_WORD
                  | ATTR_EXCLAMATION ATTR_WORD
                  | attribute_varname ATTR_EQUAL ATTR_BOOLEAN
                  | attribute_varname ATTR_EQUAL ATTR_NUMBER
                  | attribute_varname ATTR_EQUAL ATTR_STRING
                  | attribute_varname ATTR_EQUAL ATTR_WORD
                  | attribute_varname ATTR_EQUAL attributes
                  | attribute_varname ATTR_EQUAL ATTR_PLACEHOLDER
                  | attribute_varname ATTR_EQUAL math
                  | attribute_varname ATTR_EQUAL ATTR_INPUT input HYPERREF_REF_END
                  | attribute_varname ATTR_EQUAL ATTR_INPUT error
                  | ATTR_BOOLEAN
                  | ATTR_NUMBER
                  | attribute_varname
                  | ATTR_PLACEHOLDER
                  | attributes
        """
        if option == 0:
            return {'id': values[1]}
        elif option == 1:
            return {values[1]: True}
        elif option == 2:
            return {values[1]: False}
        elif option == 3:
            return {values[0]: MarkdownParser.bool(values[2])}
        elif option == 4:
            return {values[0]: MarkdownParser.num(values[2])}
        elif option == 5:
            return {values[0]: values[2][1:-1]}
        elif option == 6:
            return {values[0]: values[2]}
        elif option == 7:
            return {values[0]: values[2]}
        elif option == 8:
            return {values[0]: {'type': 'placeholder', 'command': values[2][2:-2]}}
        elif option == 9:
            return {values[0]: values[2]}
        elif option == 10:
            return {values[0]: values[3]}
        elif option == 11:
            return {values[0]: {"type":"error","exception-object":BisonSyntaxError("Error Occured in %s-Element" % (target)),"exception-type":"Syntax Error","text":values[2][0],"pos":values[2][1:]}}
        elif option == 12:
            return MarkdownParser.bool(values[0])
        elif option == 13:
            return MarkdownParser.num(values[0])
        elif option == 15:
            return {'type': 'placeholder', 'command': values[0][2:-2]}
        elif option == 16:
            return attr_dict(values[0])
        else:
            return values[0]

    def on_attribute_varname(self, target, option, names, values):
        """
        attribute_varname : ATTR_WORD
                          | ATTR_STRING
        """
        if option == 0:
            return values[0]
        return values[0][1:-1]


Parser = MarkdownParser
