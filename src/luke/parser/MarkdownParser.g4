parser grammar MarkdownParser;

options { tokenVocab=MarkdownLexer; }

input : blocks EOF ;

blocks : br? (block br?)*;
br : (NEWLINE | LINEBREAK | emptyline | HRULE)+ ;
emptyline : NEWLINE WHITESPACE* NEWLINE;

block : HRULE
      | text
      | code_block
      | headline
      | ulist
      | olist
      | quote
      | hyperref_definition
      ;

headline : HEADLINE_HASH WHITESPACE* text 
         | WHITESPACE* text WHITESPACE* (HEADLINE_ULINEDBL | HEADLINE_ULINESGL)
         ;


ulist : (ulist_elem NEWLINE)* ulist_elem;
ulist_elem : ULIST_SYM WHITESPACE* text*;
olist : (olist_elem NEWLINE)* olist_elem;
olist_elem : OLIST_SYM WHITESPACE* text*;
quote : (quote_elem NEWLINE)* quote_elem;
quote_elem : QUOTE_SYM WHITESPACE* text*;


text : (inline_element text_br)* inline_element;
text_br: NEWLINE | LINEBREAK ;

inline_element : EMPH blocks EMPH
               | STRONG blocks STRONG
               | BOLD blocks BOLD
               | ITALIC blocks ITALIC
               | code_inline
               | hyperref
               | string
//             | math
//             | latex
               ;

string : ( WORD | ANY | WHITESPACE | EXCL | HAT )+ ;

hyperref :      LSBR blocks RSBR LRBR hyperref_url RRBR # link
         | EXCL LSBR blocks RSBR LRBR hyperref_url RRBR # image
         | EXCL? LSBR string RSBR                       # reference
         | URL                                          # url
         | HAT LSBR blocks RSBR                         # inline_footnote
         | LSBR blocks RSBR HAT LSBR blocks RSBR        # positional_footnote
         | LSBR HAT blocks RSBR                         # referenc_footnote
         | EXCL LSBR blocks RSBR LRBR WHITESPACE* code_block WHITESPACE* RRBR # rendered_image
         ;
hyperref_url : ( URL | ~RRBR+ );
hyperref_definition_url : ( URL | ~WHITESPACE+ );
hyperref_definition : (IMAGE_DEFINITION | LINK_DEFINITION) WHITESPACE* (hyperref_definition_url WHITESPACE+ text?)
                    | FOOTNOTE_DEFINITION WHITESPACE* text?
                    ;

code_inline : CODE_INLINE_START CODE_INLINE_VERBATIM* CODE_INLINE_END ;
code_block : CODE_BLOCK_START CODE_BLOCK_TYPE? CODE_BLOCK_NEWLINE CODE_BLOCK_VERBATIM+ CODE_BLOCK_END ;


// TODO:
// - table
// - attributes
// - latex
// - math
