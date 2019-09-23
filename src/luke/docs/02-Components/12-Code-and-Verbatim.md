{theme=documentation}

\include{"../include.md"}

\title{Code "& Verbatim Mode"}



## Plain Markdown
Code or verbatim text is part of markdown.

Using *highlight.js*, Lukeparser supports highlighting for dozens of languages (and not-really-languages, like diffs and HTTP headers); to see the complete list, and how to write the language names, see the [highlight.min.js demo page](http://softwaremaniacs.org/media/soft/highlight/test.html).

```
Inline `code` has `back-ticks around` it.
```
\Output[
Inline `code` has `back-ticks around` it.
]

Blocks of code are fenced by lines with three back-ticks `\`\`\``.



```
\`\`\`javascript
var s = "JavaScript syntax highlighting";
alert(s);
\`\`\`
```
\Output[
```javascript
var s = "JavaScript syntax highlighting";
alert(s);
```
]

 
```
\`\`\`
No language indicated, 
so no syntax highlighting. 
\`\`\`
```
\Output[
```
No language indicated, 
so no syntax highlighting. 
```
]


## Custom Syntax
It is possible to define a custom "semantic" syntax highlighting.  
However, we will use the math-mode for that, as we would like to use latex-commands for the symantic definitions.

{.customsyntax}$$
{.customsyntax}\$\$
#include <iostream>
using namespace std;
int main()
{
    unsigned int n;
    unsigned long long factorial = 1;

    \title{\\meta\{}cout << "Enter a positive integer: ";\title{\}}
    cin >> n;

    \title{\\title\{}for(int i = 1; i <=n; ++i) \{\title{\}}
        \title{\\keyword\{}factorial *= i;\title{\}}
    \title{\\title\{}\}\title{\}}

    \title{\\meta\{}cout << "Factorial of " << n << " = " << factorial;\title{\}}
    return 0;
}
\$\$
$$
\Output[
{.customsyntax}$$
#include <iostream>
using namespace std;
int main()
{
    unsigned int n;
    unsigned long long factorial = 1;

    \meta{cout << "Enter a positive integer: ";}
    cin >> n;

    \title{for(int i = 1; i <=n; ++i) \{}
        \keyword{factorial *= i;}
    \title{\}}

    \meta{cout << "Factorial of " << n << " = " << factorial;}
    return 0;
}
$$
]

### Syntax-Commands {.collapsible}

This Tables are taken from the official [highlightjs-Documentation](https://highlightjs.readthedocs.io/en/latest/css-classes-reference.html).

**General-purpose**                                                          

| command | purpose |
| ------- | ------- |
| keyword                  | keyword in a regular Algol-style language         |
| built\_in                | built-in or library object (constant, class, function)                                         |
| type                     | user-defined type in a language with first-class syntactically significant types, like Haskell     |
| literal                  | special identifier for a built-in value ("true", "false", "null")                                  |
| number                   | number, including units and modifiers, if any.    |
| regexp                   | literal regular expression                        |
| string                   | literal string, character                         |
| subst                    | parsed section inside a literal string            |
| symbol                   | symbolic constant, interned string, goto label    |
| class                    | class or class-level declaration (interfaces, traits, modules, etc)                             |
| function                 | function or method declaration                    |
| title                    | name of a class or a function at the place of declaration                                       |
| params                   | block of function arguments (parameters) at the place of declaration                              |

**Meta**                                                                     
| command | purpose |
| ------- | ------- |
| comment                  | comment                                           |
| doctag                   | documentation markup within comments              |
| meta                     | flags, modifiers, annotations, processing instructions, preprocessor directive, etc         |
| meta-keyword             | keyword or built-in within meta construct         |
| meta-string              | string within meta construct                      |

**Tags, attributes, configs**
| command | purpose |
| ------- | ------- |
| section                  | heading of a section in a config file, heading in text markup                                       |
| tag                      | XML/HTML tag                                      |
| name                     | name of an XML tag, the first word in an s-expression                                      |
| builtin-name             | s-expression name from the language standard library                                           |
| attr                     | name of an attribute with no language defined semantics (keys in JSON, setting names in .ini), also sub-attribute within another highlighted  object, like XML tag                              |
| attribute                | name of an attribute followed by a structured value part, like CSS properties                   |
| variable                 | variable in a config or a template file, environment var expansion in a script             |

#### Special {.collapsible}
**Markup**
| command | purpose |
| ------- | ------- |
| bullet                   | list item bullet in text markup                   |
| code                     | code block in text markup                         |
| emphasis                 | emphasis in text markup                           |
| strong                   | strong emphasis in text markup                    |
| formula                  | mathematical formula in text markup               |
| link                     | hyperlink in text markup                          |
| quote                    | quotation in text markup                          |

**CSS**
| command | purpose |
| ------- | ------- |
| selector-tag             | tag selector in CSS                               |
| selector-id              | #id selector in CSS                               |
| selector-class           | .class selector in CSS                            |
| selector-attr            | [attr] selector in CSS                            |
| selector-pseudo          | :pseudo selector in CSS                           |

**Templates**
| command | purpose |
| ------- | ------- |
| template-tag             | tag of a template language                        |
| template-variable        | variable in a template language                   |

**diff**
| command | purpose |
| ------- | ------- |
| addition                 | added or changed line in a diff                   |
| deletion                 | deleted line in a diff                            |

**ReasonML**
| command | purpose |
| ------- | ------- |
| operator                 | reasonml operator such as pipe                    |
| pattern-match            | reasonml pattern matching matchers                |
| typing                   | type signatures on function parameters            |
| constructor              | type constructors                                 |
| module-access            | scope access into a ReasonML module               |
| module                   | ReasonML module reference within scope access     |



## Text-Replace

```
{emotion=happy}

\`\`\` {replace={"All work"="Only play" "no play"="no work" dull=%{emotion}%}}
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
\`\`\`
```
\Output[
{emotion=happy}

``` {replace={"All work"="Only play" "no play"="no work" dull=%{emotion}%}}
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
All work and no play makes Jake a dull boy.
```
]

## Inject Code
To inject code directly into the destination file, use the syntax `inject`.
Of course this does only work, if you know the destination view.
```
\`\`\`inject
<b>Directly injected</b>
\`\`\`
```
\Output[
```inject
<b>Directly injected</b>
```
]

Using [control flow commands](../04-Commands/01-Control-Flow.md) it is possible
to specify the inject code based on the view.
```latex
\ifeq{%{view}% html}[
	\`\`\`inject
	<b>Directly injected HTML.</b>
	\`\`\`
][
	\`\`\`inject
	\textbf{Directly injected LaTeX.}
	\`\`\`
]
```
\Output[
\ifeq{%{view}% html}[
	```inject
	<b>Directly injected HTML.</b>
	```
][
	```inject
	\textbf{Directly injected LaTeX.}
	```
]
]
