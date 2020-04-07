lexer grammar MarkdownLexer;

// comments
BC  : '/*' .*? ( '*/' | EOF ) -> channel(HIDDEN) ;
LC  : '//' ~[\r\n]* -> channel(HIDDEN) ;

CODE_INLINE_START         : '`' -> pushMode(CodeInlineVerbatim) ;
CODE_BLOCK_START          : '```' -> pushMode(CodeBlockSettings) ;

LINKURL: (('https://'|'ftp://'|'http://'|'www.') ~[)]+);
URL: (('https://'|'ftp://'|'http://'|'www.') ~[ \t]+) | ('<' ('https://'|'ftp://'|'http://'|'www.') ~[>]+ '>') ;

HEADLINE_HASH: '#'+ ;
HEADLINE_ULINEDBL: NEWLINE '=''=''='+ ;
HEADLINE_ULINESGL: NEWLINE '-''-''-'+ ;

HRULE : NEWLINE NEWLINE '__' '_'+ | NEWLINE NEWLINE '--' '-'+ | NEWLINE NEWLINE '**' '*'+ ;

ULIST_SYM: ('-' | '*' | '+') ('[' ~[\]]+ ']' )? ;
OLIST_SYM: [ivxcdmlIVXCDML0-9]+ '.';
QUOTE_SYM: '>';

STRONG : '**' ;
BOLD : '__' ;
EMPH : '*' ;
ITALIC : '_' ;

EXCL: '!' ;
HAT: '^' ;
LSBR : '[' NEWLINE* ;
RSBR : NEWLINE* ']' ;
LRBR : '(' NEWLINE* ;
RRBR : NEWLINE* ')' ;

ESCAPED : '\\' ( EMPH | ITALIC | '`' | LSBR | RSBR | LRBR | RRBR ) ;
NEWLINE             : ('\r'? '\n' | '\r') ;
LINEBREAK           : '  ' NEWLINE ;
WHITESPACE          : (' ' | '\t')+ ;
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
