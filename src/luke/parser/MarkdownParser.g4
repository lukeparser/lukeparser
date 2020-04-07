parser grammar MarkdownParser;

options { tokenVocab=MarkdownLexer; }

input : block* EOF ;
block : text
      | code_block
      ;


/*
span  : '**' span '**' # strong
      | '__' span '__' # bold
      | '*'  span '*'  # emph
      | '_'  span '_'  # italic
      | string+ span+  # text_span
      | string+ span+ string # text_span
      | string+        # text
      ;
*/

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

string : ( WORD | ANY | WHITESPACE | EXCL | HAT )+? ;
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



