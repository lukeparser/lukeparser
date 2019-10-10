{theme=documentation}

\include{"../include.md"}

\title{"Predefined Commands" "Various"}



## Include Documents
This includes another document into any specifiy place.
```latex
\include{"path/to/document"}
```


## Date
See [strftime](http://strftime.org/) for a Reference of all directives.

```latex
\date  

\date{"%c"}  

\date{"%x"}  

\date{"%X"}  

\date{"%d.%m.%y"}
```
\Output[
\date  

\date{"%c"}  

\date{"%x"}  

\date{"%X"}  

\date{"%d.%m.%y"}
]


## Last Document Change
Prints the last time this document was changed. Uses the same directives as the data-command above.
```latex
\lastchange

\lastchange{"%c"}
```
\Output[
\lastchange

\lastchange{"%c"}
]


## List Documents in Current directory
Lists all documents in current directory and marks the current one.
```
\listdocuments(filter="[0-9]+-?(.*)((.md)|/)",sub="\\1"):
```

```
**Plain**
\listdocuments

**Other Base Directory**
\listdocuments{basepath="."}
```
\Output[
**Plain**
\listdocuments

**Other Base Directory**
\listdocuments{basepath="."}
]






## Icons
See [Extra-Components/Icons](../03-Extra-Components/03-Icons.md).
```latex
\icon{headphones} + \icon{musical-note} = \icon{heart}
```
\Output[
\icon{headphones} + \icon{musical-note} = \icon{heart}
]


## Redirect (HTML-only)
Redirect the current page somewhere else.
```latex
\redirect{"otherfile.md"}
```


## Simple Helpers

**New Line Command**
This command comes handy in places that do not allow block-elements.
```
### Section \n with \n new line characters
```
\Output[
### Section \n with \n new line characters
]



**Block**
This command comes handy in places that do not allow block-elements.
```
| Key | Value |
| --- | ----- |
| Key | Value |
| Key | \block[
	Wow. It's a block with new lines.  

	**Test**
] |
| Key | Value |
```
\Output[
| Key | Value |
| --- | ----- |
| Key | Value |
| Key | \block[
	Wow. It's a block with new lines.  

	**Test**
] |
| Key | Value |
]



## Footnotes
Flush all current footnotes. See [Footnotes Section](../02-Components/05-Footnotes-and-Notes.md) for more details.

## Components
This is a theme-specific command. Goto [Themes and Views](../05-Themes-and-Views/index.md) to find out more.


## arXiv
For scientific work, the use with arxiv is essential. Lukeparser can grep for you all the metadata.
```
\arxiv{"hep-th/9711200"}
```
\Output[
    \arxiv{"hep-th/9711200"}
]


## Luke Version
```
\version
```
\Output[
    \version
]



