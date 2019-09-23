{theme=documentation}

\include{"../include.md"}

\title{Markdown Overview}

\newcommand{Output}[
# Results in {.collapsible}
%{arg0}%
]



This is a very short reference for the most used features of Markdown.
For more complete info, see [John Gruber's original spec](http://daringfireball.net/projects/markdown/) and the [Github-flavored Markdown info page](http://github.github.com/github-flavored-markdown/).

Note, that no Lukeparser features are used herin.
If you know Markdown already, feel free to skip this list.
Every Section contains its output right below the code in a collapsed box.

So let's begin.


### About Markdown

Markdown is a way to format Text -- very easily.
So easy that you can just start to write.

Formatting is getting more interesting; how to emphasize Text, embedding Images or including Tables?

See the guide below, for the most common Markdown syntax.


## Headers

```
# This is an h1-tag
## This is an h2-tag
###### This is an h6-tag

Nicer Header H1
===============

Nicer Header H2
---------------
```
\Output[
# This is an h1-tag {section-contentlist=False}
## This is an h2-tag {section-contentlist=False}
###### This is an h6-tag {section-contentlist=False}


Nicer Header H1 {section-contentlist=False}
===============

Nicer Header H2 {section-contentlist=False}
---------------
]



## Paragraphs & New Lines

```
First Line.
As well in first Line. (This Line ends with two Spaces)  
Second Line.

New Paragraph.

---
This text is seperated by a horizontal line. Note the empty line above the three Hyphens, 
otherwise ”new Paragraph“ would be a Header.  
Instead, you can also use three or more Underscores `_` or Stars `*`.
```
\Output[
First Line.
As well in first Line. (This Line ends with two Spaces)  
Second Line.

New Paragraph.

---
This text is seperated by a horizontal line. Note the empty line above the three Hyphens,
otherwise ”new Paragraph“ would be a Header.  
Instead, you can also use three or more Underscores `_` or Stars `*`.
]


## Emphasis
```
*This text will be italic*
_This will also be italic_

**This text will be bold**
__This will also be bold__

_You **can** combine them_.
~~Or just strike it.~~
```
\Output[
*This text will be italic*  
_This will also be italic_

**This text will be bold**  
__This will also be bold__

_You **can** combine them_  
~~Or just strike it.~~
]




## Lists (unordered)

```
* Item 1
* Item 2
  * Item 2a
  * Item 2b
```
\Output[
* Item 1
* Item 2
  * Item 2a
  * Item 2b
]

## Lists (ordered)

```
1. Item 1
1. Item 2
1. Item 3
   1. Item 3a
   1. Item 3b
```
\Output[
1. Item 1
1. Item 2
1. Item 3
   1. Item 3a
   1. Item 3b
]

## Images

```
![Lukeparser Logo](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/)
```
\Output[
![Lukeparser Logo](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/)
]

## Links

```
http://github.com - automatic!  
[GitHub](http://github.com)
```
\Output[
http://github.com - automatic!  
[GitHub](http://github.com)
]

## Blockquotes

```markdown
As Yoda said:

> Do. Or do not. 
> There is no try.
```
\Output[
As Yoda said:

> Do. Or do not. 
> There is no try.
]


## Comments
```markdown
// This is a comment and will not appear in the result.

This will apear again.  
/*
This is a multiline comment.
/*
You can nest them if you want.
*/ 

*/ 
This will apear again, too.
```
\Output[
// This is a comment and will not appear in the result.

This will apear again.  
/*
This is a multiline comment.
/*
You can nest them if you want.
*/ 

*/ 
This will apear again, too.
]

