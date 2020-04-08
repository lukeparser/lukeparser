lexer grammar MarkdownLexer;

/*
@lexer::header{
from antlr4.Token import CommonToken
import re
import importlib
# Allow languages to extend the lexer and parser, by loading the parser dynamically
module_path = __name__[:-5]
language_name = __name__.split('.')[-1]
language_name = language_name[:-5]  # Remove Lexer from name
LanguageParser = getattr(importlib.import_module('{}Parser'.format(module_path)), '{}Parser'.format(language_name))
}

@lexer::members {
@property
def tokens(self):
    try:
        return self._tokens
    except AttributeError:
        self._tokens = []
        return self._tokens
@property
def indents(self):
    try:
        return self._indents
    except AttributeError:
        self._indents = []
        return self._indents
@property
def opened(self):
    try:
        return self._opened
    except AttributeError:
        self._opened = 0
        return self._opened
@opened.setter
def opened(self, value):
    self._opened = value
@property
def lastToken(self):
    try:
        return self._lastToken
    except AttributeError:
        self._lastToken = None
        return self._lastToken
@lastToken.setter
def lastToken(self, value):
    self._lastToken = value
def reset(self):
    super().reset()
    self.tokens = []
    self.indents = []
    self.opened = 0
    self.lastToken = None
def emitToken(self, t):
    super().emitToken(t)
    self.tokens.append(t)
def nextToken(self):
    if self._input.LA(1) == Token.EOF and self.indents:
        for i in range(len(self.tokens)-1,-1,-1):
            if self.tokens[i].type == Token.EOF:
                self.tokens.pop(i)
        self.emitToken(self.commonToken(LanguageParser.NEWLINE, '\n'))
        while self.indents:
            self.emitToken(self.createDedent())
            self.indents.pop()
        self.emitToken(self.commonToken(LanguageParser.EOF, "<EOF>"))
    next = super().nextToken()
    if next.channel == Token.DEFAULT_CHANNEL:
        self.lastToken = next
    return next if not self.tokens else self.tokens.pop(0)
def createDedent(self):
    dedent = self.commonToken(LanguageParser.DEDENT, "")
    dedent.line = self.lastToken.line
    return dedent
def commonToken(self, type, text, indent=0):
    stop = self.getCharIndex()-1-indent
    start = (stop - len(text) + 1) if text else stop
    return CommonToken(self._tokenFactorySourcePair, type, super().DEFAULT_TOKEN_CHANNEL, start, stop)
@staticmethod
def getIndentationCount(spaces):
    count = 0
    for ch in spaces:
        if ch == '\t':
            count += 8 - (count % 8)
        else:
            count += 1
    return count
def atStartOfInput(self):
    return Lexer.column.fget(self) == 0 and Lexer.line.fget(self) == 1
}
*/



// comments
BC  : '/*' .*? ( '*/' | EOF ) -> channel(HIDDEN) ;
LC  : '//' ~[\r\n]* -> channel(HIDDEN) ;

CODE_INLINE_START         : '`' -> pushMode(CodeInlineVerbatim) ;
CODE_BLOCK_START          : '```' -> pushMode(CodeBlockSettings) ;
MATH_INLINE_START          : '$' ANYWS -> pushMode(MathInline);
MATH_BLOCK_START          : '$$' -> pushMode(MathBlock);

URL: (('https://'|'ftp://'|'http://'|'www.') ~[ \t\n\r)]+) | ('<' ( '\\>' | . )+? '>') ;

FOOTNOTE_DEFINITION : ( '^[' | '[^' ) ('\\]' | . )+? ']:' ;
IMAGE_DEFINITION    : '![' ('\\]' | . )+? ']:' ;
LINK_DEFINITION     : '[' ('\\]' | . )+? ']:' ;

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

NEWLINE : ( '\r'? '\n' | '\r' | '\f' ) ;
/*
NEWLINE
 : ( {self.atStartOfInput()}?   WHITESPACE | ( '\r'? '\n' | '\r' | '\f' ) WHITESPACE?)
   {
tempt = Lexer.text.fget(self)
newLine = re.sub("[^\r\n\f]+", "", tempt)
spaces = re.sub("[\r\n\f]+", "", tempt)
la_char = ""
try:
    la = self._input.LA(1)
    la_char = chr(la)       # Python does not compare char to ints directly
except ValueError:          # End of file
    pass
# Strip newlines inside open clauses except if we are near EOF. We keep NEWLINEs near EOF to
# satisfy the final newline needed by the single_put rule used by the REPL.
try:
    nextnext_la = self._input.LA(2)
    nextnext_la_char = chr(nextnext_la)
except ValueError:
    nextnext_eof = True
else:
    nextnext_eof = False
if self.opened > 0 or nextnext_eof is False and (la_char == '\r' or la_char == '\n' or la_char == '\f' or la_char == '#'):
    self.skip()
else:
    indent = self.getIndentationCount(spaces)
    previous = self.indents[-1] if self.indents else 0
    self.emitToken(self.commonToken(self.NEWLINE, newLine, indent=indent))      # NEWLINE is actually the '\n' char
    if indent == previous:
        self.skip()
    elif indent > previous:
        self.indents.append(indent)
        self.emitToken(self.commonToken(LanguageParser.INDENT, spaces))
    else:
        while self.indents and self.indents[-1] > indent:
            self.emitToken(self.createDedent())
            self.indents.pop()
    }
 ;
 */

/*
NEWLINE
 : ( {atStartOfInput()}?   WHITESPACE
   | ( '\r'? '\n' | '\r' ) WHITESPACE?
   )
   {
     String newLine = getText().replaceAll("[^\r\n]+", "");
     String spaces = getText().replaceAll("[\r\n]+", "");
     int next = _input.LA(1);
     if (opened > 0 || next == '\r' || next == '\n' || next == '#') {
       // If we're inside a list or on a blank line, ignore all indents, 
       // dedents and line breaks.
       skip();
     }
     else {
       emit(commonToken(NEWLINE, newLine));
       int indent = getIndentationCount(spaces);
       int previous = indents.isEmpty() ? 0 : indents.peek();
       if (indent == previous) {
         // skip indents of the same size as the present indent-size
         skip();
       }
       else if (indent > previous) {
         indents.push(indent);
         emit(commonToken(Python3Parser.INDENT, spaces));
       }
       else {
         // Possibly emit more than 1 DEDENT token.
         while(!indents.isEmpty() && indents.peek() > indent) {
           this.emit(createDedent());
           indents.pop();
         }
       }
     }
   }
 ;*/

ESCAPED : '\\' ( EMPH | ITALIC | '`' | LSBR | RSBR | LRBR | RRBR | '\\' | '<' ) ;
LINEBREAK           : '  ' NEWLINE ;
WHITESPACE          : [ \t]+ ;
fragment ANYWS      : ( WHITESPACE | NEWLINE )* ;
WORD                : ( [a-z] | [A-Z] )+ ;
ANY                 : .;


mode CodeInlineVerbatim;
CODE_INLINE_END         : '`' -> popMode;
CODE_INLINE_VERBATIM   : ('\\`' | ~[`] )+;

mode CodeBlockSettings;
CODE_BLOCK_LCBR        : '{' -> pushMode(Attributes);
CODE_BLOCK_TYPE        : ~[ \n\r{]+;
CODE_BLOCK_NEWLINE     : ('\r'? '\n' | '\r')+ -> pushMode(CodeBlockVerbatim) ;
CODE_BLOCK_WHITESPACE  : (' ' | '\t')+ -> skip;

mode CodeBlockVerbatim;
CODE_BLOCK_END         : '```' -> popMode, popMode;
CODE_BLOCK_VERBATIM   : ('\\`' | . )+? -> more;

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
ATTR_STRING: '"' ( '\\"' | . )*? '"' | '\'' ( '\\"' | . )*? '\'' ;
ATTR_WORD  : ( [a-z] | [A-Z] | '-' ) + ;
ATTR_LSBR : '[' -> pushMode(DEFAULT_MODE) ;
ATTR_CMD : '\\' ATTR_WORD ( '.' ATTR_WORD )*
         | '\\(' ATTR_WORD ( '.' ATTR_WORD )* ')' ;
ATTR_ESCAPE : '\\' ( ATTR_HASH | ATTR_DOT | ATTR_LSBR ) ;
ATTR_WHITESPACE : (',' | ' ' | '\t' | ('\r'? '\n' | '\r') )+ -> skip ;
ATTR_LCBR : '{' -> pushMode(Attributes);
ATTR_RCBR : '}' -> popMode;
