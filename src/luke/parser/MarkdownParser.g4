parser grammar MarkdownParser;

options { tokenVocab=MarkdownLexer; }

input : blocks EOF ;

blocks : br? (block br?)*;
br : (NEWLINE | LINEBREAK | emptyline | HRULE)+ ;
emptyline : NEWLINE WHITESPACE* NEWLINE;
ws : ( WHITESPACE | NEWLINE )* ;

block : HRULE
      | text
      | code_block
      | headline
      | ulist
      | olist
      | quote
      | hyperref_definition
      | table
      | math_block
      | attributes emptyline
      | attributes (ws block)?
      ;

headline : HEADLINE_HASH WHITESPACE* text WHITESPACE* attributes? WHITESPACE*
         | WHITESPACE* text WHITESPACE* attributes? WHITESPACE* (HEADLINE_ULINEDBL | HEADLINE_ULINESGL)
         ;


ulist : ulist_elem (NEWLINE ulist_elem )* ;
ulist_elem : ULIST_SYM WHITESPACE* text* WHITESPACE* attributes?;
olist : olist_elem (NEWLINE olist_elem )* ;
olist_elem : OLIST_SYM WHITESPACE* text* WHITESPACE* attributes?;
quote : quote_elem (NEWLINE quote_elem )* ;
quote_elem : QUOTE_SYM WHITESPACE* text* WHITESPACE* attributes?;


text : (inline_element text_br)* inline_element;
text_br: NEWLINE | LINEBREAK ;

inline_element : EMPH blocks EMPH
               | STRONG blocks STRONG
               | BOLD blocks BOLD
               | ITALIC blocks ITALIC
               | code_inline
               | hyperref
               | string
               | math_inline
               | cmd
               | attributes inline_element
               ;

string : ( WORD | ANY | WHITESPACE | EXCL | HAT | ESCAPED )+ ;

hyperref :      LSBR blocks RSBR LRBR hyperref_url RRBR # link
         | EXCL LSBR blocks RSBR LRBR hyperref_url RRBR # image
         | EXCL? LSBR string RSBR                       # reference
         | URL                                          # url
         | HAT LSBR blocks RSBR                         # inline_footnote
         | LSBR blocks RSBR HAT LSBR blocks RSBR        # positional_footnote
         | LSBR HAT blocks RSBR                         # referenc_footnote
         | EXCL LSBR blocks RSBR LRBR ws code_block ws RRBR # rendered_image
         ;
hyperref_url : ( URL | ~RRBR+ );
hyperref_definition_url : ( URL | ~WHITESPACE+ );
hyperref_definition : (IMAGE_DEFINITION | LINK_DEFINITION) ws (hyperref_definition_url ws text?)
                    | FOOTNOTE_DEFINITION ws text?
                    ;

code_inline : CODE_INLINE_START CODE_INLINE_VERBATIM* CODE_INLINE_END ;
code_block : CODE_BLOCK_START CODE_BLOCK_TYPE? attributes? CODE_BLOCK_NEWLINE CODE_BLOCK_VERBATIM* CODE_BLOCK_END ;

table : (table_row | table_separator_row)+ ;
table_row : TABLE_DELIM? (text TABLE_DELIM)+ text TABLE_DELIM? NEWLINE? ;
table_separator_row : TABLE_DELIM? (table_separator TABLE_DELIM)+ table_separator TABLE_DELIM? NEWLINE? ;
table_separator : attributes? ( TABLE_HRULE | TABLE_HRULE_CENTERED | TABLE_HRULE_LEFT_ALIGNED | TABLE_HRULE_RIGHT_ALIGNED ) ;

cmd : CMD attributes? cmd_arg* ;
cmd_arg : LSBR blocks RSBR ;

math_inline : MATH_INLINE_START math_text+ MATH_INLINE_END ;
math_block : MATH_BLOCK_START math_text+ MATH_BLOCK_END ;
math_text : math_cmd | ( MATH_INLINE_CHAR | MATH_BLOCK_CHAR )+ | ( ( MATH_INLINE_LCBR | MATH_BLOCK_LCBR ) math_text? ( MATH_INLINE_RCBR | MATH_BLOCK_RCBR ) ) ;
math_cmd : ( MATH_INLINE_CMD | MATH_BLOCK_CMD ) ( ( MATH_INLINE_LCBR | MATH_BLOCK_LCBR ) math_text? ( MATH_INLINE_RCBR | MATH_BLOCK_RCBR ) )* ;


attributes: ( LCBR | ATTR_LCBR | CODE_BLOCK_LCBR ) attribute* ATTR_RCBR;
attribute : ATTR_HASH ATTR_WORD
          | ATTR_DOT ATTR_WORD
          | ATTR_EXCL ATTR_WORD
          | attribute_name ATTR_EQUAL attribute_value
          | attribute_value
          ;
attribute_name  :  ATTR_WORD | ATTR_STRING ;
attribute_value :  ATTR_WORD | ATTR_STRING | ATTR_BOOL | ATTR_NUMBER | ATTR_CMD | attributes | attribute_blocks ;
attribute_blocks : ATTR_LSBR blocks RSBR ;
