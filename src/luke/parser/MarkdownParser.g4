parser grammar MarkdownParser;

options { tokenVocab=MarkdownLexer; }

input : block* EOF ;
block : text
      | code_block
      | headline
      | ulist
      | olist
      | quote
      ;

headline : HEADLINE_HASH WHITESPACE* string 
         | WHITESPACE* string WHITESPACE* (HEADLINE_ULINEDBL | HEADLINE_ULINESGL)
         ;


ulist : (ulist_elem NEWLINE)* ulist_elem;
ulist_elem : ULIST_SYM WHITESPACE* text*;
olist : (olist_elem NEWLINE)* olist_elem;
olist_elem : OLIST_SYM WHITESPACE* text*;
quote : (quote_elem NEWLINE)* quote_elem;
quote_elem : QUOTE_SYM WHITESPACE* text*;


text : inline_element+
     ;

inline_element : EMPH block* EMPH?
               | STRONG block* STRONG?
               | BOLD block* BOLD?
               | ITALIC block* ITALIC?
               | code_inline
               | hyperref
               | string
//             | math
//             | latex
               ;

string : ( WORD | ANY | WHITESPACE | EXCL | HAT )+ ;
hyperref :      LSBR block* RSBR LRBR hyperref_url RRBR # link
         | EXCL LSBR block* RSBR LRBR hyperref_url RRBR # image
         | EXCL? LSBR string RSBR                       # reference
         | URL                                          # url
         | HAT LSBR block* RSBR                         # inline_footnote
         | LSBR block* RSBR HAT LSBR block* RSBR        # positional_footnote
         | LSBR HAT block* RSBR                         # referenc_footnote
         | EXCL LSBR block* RSBR LRBR WHITESPACE* code_block WHITESPACE* RRBR # rendered_image
         ;

hyperref_url : ( LINKURL | ~RRBR+ );

code_inline : CODE_INLINE_START CODE_INLINE_VERBATIM* CODE_INLINE_END ;
code_block : CODE_BLOCK_START CODE_BLOCK_TYPE? CODE_BLOCK_NEWLINE CODE_BLOCK_VERBATIM+ CODE_BLOCK_END ;



