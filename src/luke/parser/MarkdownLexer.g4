lexer grammar MarkdownLexer;

// comments
BC  : '/*' .*? ( '*/' | EOF ) -> channel(HIDDEN) ;
LC  : '//' ~[\r\n]* -> channel(HIDDEN) ;

CODE_INLINE_START         : '`' -> pushMode(CodeInlineVerbatim) ;
CODE_BLOCK_START          : '```' -> pushMode(CodeBlockSettings) ;
MATH_INLINE_START          : '$' ANYWS -> pushMode(MathInline);
MATH_BLOCK_START          : '$$' -> pushMode(MathBlock);

URL: (('https://'|'ftp://'|'http://'|'www.') ~[ \t\n\r)]+) | ('<' ('https://'|'ftp://'|'http://'|'www.') ~[>]+ '>') ;

FOOTNOTE_DEFINITION : ( '^[' | '[^' ) ~[\]]+ ']:' ;
IMAGE_DEFINITION    : '![' ~[\]]+ ']:' ;
LINK_DEFINITION     : '[' ~[\]]+ ']:' ;

HEADLINE_HASH: '#'+ ;
HEADLINE_ULINEDBL: NEWLINE '=''=''='+ ;
HEADLINE_ULINESGL: NEWLINE '-''-''-'+ ;

HRULE : NEWLINE NEWLINE '__' '_'+ | NEWLINE NEWLINE '--' '-'+ | NEWLINE NEWLINE '**' '*'+ ;

ULIST_SYM: ('-' | '*' | '+') WHITESPACE+ ('[' ~[\]]+ ']' )? ;
OLIST_SYM: [ivxcdmlIVXCDML0-9]+ '.' WHITESPACE+ ;
QUOTE_SYM: '>' WHITESPACE+ ;

STRONG : '**' ;
BOLD : '__' ;
EMPH : '*' ;
ITALIC : '_' ;

CMD : '\\' WORD ( '.' WORD )*
    | '\\(' WORD ( '.' WORD )* ')' ;

EXCL: '!' ;
HAT: '^' ;
LSBR : '[' ANYWS -> pushMode(DEFAULT_MODE) ;
RSBR : ANYWS ']' -> popMode ;
LRBR : '(' ANYWS ;
RRBR : ANYWS ')' ;
LCBR : '{' -> pushMode(Attributes);

TABLE_DELIM               : WHITESPACE* '|' WHITESPACE* ;
TABLE_HRULE               : WHITESPACE* ('--' '-'+ | '++' '+'+) WHITESPACE* ;
TABLE_HRULE_LEFT_ALIGNED  : WHITESPACE* ':' '--' '-'+     WHITESPACE* ;
TABLE_HRULE_CENTERED      : WHITESPACE* ':' '--' '-'+ ':' WHITESPACE* ;
TABLE_HRULE_RIGHT_ALIGNED : WHITESPACE*     '--' '-'+ ':' WHITESPACE* ;

ESCAPED : '\\' ( EMPH | ITALIC | '`' | LSBR | RSBR | LRBR | RRBR | '\\' ) ;
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
CODE_BLOCK_LCBR        : '{' -> pushMode(Attributes);
CODE_BLOCK_TYPE        : ~[ \n\r{]+;
CODE_BLOCK_NEWLINE     : ('\r'? '\n' | '\r')+ -> pushMode(CodeBlockVerbatim) ;
CODE_BLOCK_WHITESPACE  : (' ' | '\t')+ -> skip;

mode CodeBlockVerbatim;
CODE_BLOCK_END         : '```' -> popMode, popMode;
CODE_BLOCK_VERBATIM   : ~[`]+;

mode MathInline;
MATH_INLINE_LCBR : '{' ;
MATH_INLINE_RCBR : '}' ;
fragment MATH_INLINE_NEWLINE             : ('\r'? '\n' | '\r') ;
fragment MATH_INLINE_WHITESPACE          : (' ' | '\t')+ ;
MATH_INLINE_END  : ( MATH_INLINE_WHITESPACE | MATH_INLINE_NEWLINE )* '$' -> popMode ;
MATH_INLINE_CMD : '\\' WORD ;
MATH_INLINE_CHAR : ~[\\$\r\n\t{}]+ | MATH_INLINE_ESCAPED | MATH_INLINE_NEWLINE | MATH_INLINE_WHITESPACE ;
fragment MATH_INLINE_ESCAPED : '\\' ( MATH_INLINE_LCBR | MATH_INLINE_RCBR | MATH_INLINE_END | '\\' ) ;

mode MathBlock;
MATH_BLOCK_LCBR : '{' ;
MATH_BLOCK_RCBR : '}' ;
fragment MATH_BLOCK_NEWLINE             : ('\r'? '\n' | '\r') ;
fragment MATH_BLOCK_WHITESPACE          : (' ' | '\t')+ ;
MATH_BLOCK_END  : ( MATH_BLOCK_WHITESPACE | MATH_BLOCK_NEWLINE )* '$$' -> popMode ;
MATH_BLOCK_CMD : '\\' WORD ;
MATH_BLOCK_CHAR : ~[\\$\r\n\t{}]+ | MATH_BLOCK_ESCAPED | MATH_BLOCK_NEWLINE | MATH_BLOCK_WHITESPACE ;
fragment MATH_BLOCK_ESCAPED : '\\' ( MATH_BLOCK_LCBR | MATH_BLOCK_RCBR | MATH_BLOCK_END | '\\' ) ;


mode Attributes;
ATTR_HASH  : '#' ;
ATTR_DOT   : '.' ;
ATTR_EXCL  : '!' ;
ATTR_EQUAL : '=' | ':' ;
ATTR_BOOL  : [Tt]'rue'? [Ff]'alse'? ;
ATTR_NUMBER: [0-9]+([.,][0-9]+)? ;
ATTR_STRING: '"' ~["]+ '"' | '\'' ~[']+ '\'' ;
ATTR_WORD  : ( [a-z] | [A-Z] ) + ;
ATTR_LSBR : '[' -> pushMode(DEFAULT_MODE) ;
ATTR_CMD : '\\' ATTR_WORD ( '.' ATTR_WORD )*
         | '\\(' ATTR_WORD ( '.' ATTR_WORD )* ')' ;
ATTR_ESCAPE : '\\' ( ATTR_HASH | ATTR_DOT | ATTR_LSBR ) ;
ATTR_WHITESPACE : (',' | ' ' | '\t' | ('\r'? '\n' | '\r') )+ -> skip ;
ATTR_LCBR : '{' -> pushMode(Attributes);
ATTR_RCBR : '}' -> popMode;

// [\]] not possible to escape
