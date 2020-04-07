lexer grammar MarkdownLexer;

// comments
BC  : '/*' .*? ( '*/' | EOF ) -> channel(HIDDEN) ;
LC  : '//' ~[\r\n]* -> channel(HIDDEN) ;

CODE_INLINE_START         : '`' -> pushMode(CodeInlineVerbatim) ;
CODE_BLOCK_START          : '```' -> pushMode(CodeBlockSettings) ;
MATHINLINE_START          : '$' ANYWS -> pushMode(MathInline);
/* MATH_BLOCK_START          : '$$' -> pushMode(MathBlock); */

URL: (('https://'|'ftp://'|'http://'|'www.') ~[ \t\n\r)]+) | ('<' ('https://'|'ftp://'|'http://'|'www.') ~[>]+ '>') ;

FOOTNOTE_DEFINITION : ( '^[' | '[^' ) ~[\]]+ ']:' ;
IMAGE_DEFINITION    : '![' ~[\]]+ ']:' ;
LINK_DEFINITION     : '[' ~[\]]+ ']:' ;

HEADLINE_HASH: '#'+ ;
HEADLINE_ULINEDBL: NEWLINE '=''=''='+ ;
HEADLINE_ULINESGL: NEWLINE '-''-''-'+ ;

HRULE : NEWLINE NEWLINE '__' '_'+ | NEWLINE NEWLINE '--' '-'+ | NEWLINE NEWLINE '**' '*'+ ;

ULIST_SYM: ('-' | '*' | '+') ' ' ('[' ~[\]]+ ']' )? ;
OLIST_SYM: [ivxcdmlIVXCDML0-9]+ '. ';
QUOTE_SYM: '> ';

STRONG : '**' ;
BOLD : '__' ;
EMPH : '*' ;
ITALIC : '_' ;

CMD : '\\' WORD ( '.' WORD )*
    | '\\(' WORD ( '.' WORD )* ')' ;

EXCL: '!' ;
HAT: '^' ;
LSBR : '[' ANYWS ;
RSBR : ANYWS ']' ;
LRBR : '(' ANYWS ;
RRBR : ANYWS ')' ;

TABLE_DELIM               : WHITESPACE* '|' WHITESPACE* ;
TABLE_HRULE               : WHITESPACE* ('--' '-'+ | '++' '+'+) WHITESPACE* ;
TABLE_HRULE_LEFT_ALIGNED  : WHITESPACE* ':' '--' '-'+     WHITESPACE* ;
TABLE_HRULE_CENTERED      : WHITESPACE* ':' '--' '-'+ ':' WHITESPACE* ;
TABLE_HRULE_RIGHT_ALIGNED : WHITESPACE*     '--' '-'+ ':' WHITESPACE* ;

ESCAPED : '\\' ( EMPH | ITALIC | '`' | LSBR | RSBR | LRBR | RRBR ) ;
NEWLINE             : ('\r'? '\n' | '\r') ;
LINEBREAK           : '  ' NEWLINE ;
WHITESPACE          : (' ' | '\t')+ ;
fragment ANYWS      : ( WHITESPACE | NEWLINE )* ;
WORD                : ( [a-z] | [A-Z] )+ ;
ANY                 : .;


mode CodeInlineVerbatim;
CODE_INLINE_END         : '`' -> popMode;
CODE_INLINE_VERBATIM    : ~[`]+;

mode CodeBlockSettings;
CODE_BLOCK_TYPE        : ~[ \n\r]+;
CODE_BLOCK_NEWLINE     : ('\r'? '\n' | '\r')+ -> pushMode(CodeBlockVerbatim) ;
CODE_BLOCK_WHITESPACE  : (' ' | '\t')+ -> skip;

mode CodeBlockVerbatim;
CODE_BLOCK_END         : '```' -> popMode, popMode;
CODE_BLOCK_VERBATIM   : ~[`]+;

mode MathInline;
MATHINLINE_LCBR : '{' ;
MATHINLINE_RCBR : '}' ;
fragment MATHINLINE_NEWLINE             : ('\r'? '\n' | '\r') ;
fragment MATHINLINE_WHITESPACE          : (' ' | '\t')+ ;
MATHINLINE_END  : ( MATHINLINE_WHITESPACE | MATHINLINE_NEWLINE )* '$' -> popMode ;
MATHINLINE_CMD : '\\' WORD ( '.' WORD )* ;
MATHINLINE_CHAR : ~[\\$\r\n\t]+ | MATHINLINE_ESCAPED | MATHINLINE_NEWLINE | MATHINLINE_WHITESPACE ;
fragment MATHINLINE_ESCAPED : '\\' ( MATHINLINE_LCBR | MATHINLINE_RCBR | MATHINLINE_END ) ;

/* mode MathBlock; */

//mode Attributes;


// TODO: read linkurl using mode
// TODO: lists with whitespace instead of space
