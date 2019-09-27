{theme=documentation}

\include{"../include.md"}

\title{Sections "and their Settings"}



## Pure Markdown

```
# H1
## H2
### H3
#### H4
## H2
## H2
## H2
##### H5
###### H6

Alternatively, for H1 and H2, an underline-ish style:

Alt-H1
======

Alt-H2
------
```

\Output[
# H1 {!section-contentlist}
## H2 {!section-contentlist}
### H3 {!section-contentlist}
#### H4 {!section-contentlist}
##### H5 {!section-contentlist}
#### H4 {!section-contentlist}
###### H6 {!section-contentlist}

Alternatively, for H1 and H2, an underline-ish style:

Alt-H1 {!section-contentlist}
======

Alt-H2  {!section-contentlist}
------
]


## Passing Attributes
More settings can be given to a heading using either
```
# H1 {var=42}

H1 {var=42}
===========
```
or
```
{var=42}
# H1
```


## Section Counter
```
{.section-counter}

### Section 1

### Section 2

### Section 3

### Section 3

```
\Output[
{.section-counter}

### Section 1

### Section 2

### Section 3

### Section 3
]


// should be queried from user-config defaults in the future
{section={
alignment=left
section-auto-id=T
section-counter=F
section-contentlist=T
}}

## Predefined Attributes

### Always
| Variable | Function |
| --- | --- |
| `alignment` | \block[ Adjust alignment of heading.  
**Default**: {verbatim=%{section.alignment}%}``

	**Possible Values**: 
	- `centered`/`center`
	- `left`/`normal`
	- `right`
] |
| `section-auto-id` | \block[ Adds an automatically generated string as an unique identifier for that section.  
**Default**: {verbatim=%{section.section-auto-id}%}``

	**Possible Values**: 
	- `True` or `False`
] |
| `section-counter` | \block[ Adds a counter to the section.  
**Default**: {verbatim=%{section.section-counter}%}``

	**Possible Values**: 
	- `True` or `False`
] |
| `section-contentlist` | \block[ Adds this section to the contentlist.  
**Default**: {verbatim=%{section.section-contentlist}%}``

	**Possible Values**: 
	- `True` or `False`
] |
| `hidden` | \block[ Hides this Section from output.  
**Default**: `True`

	**Possible Values**: 
	- `True` or `False`
] |

#### Internal Attribute Names {.collapsible}

| Variable | Function |
| --- | --- |
| `type` | `section` |
| `content` | The text of a section. |
| `title` | The title of a section. |
| `h-level` | The level of a section. (h1,h2,etc.) |
| `level` | The intendation-level. (only used for preprocessing) |

### HTML-View
| Variable | Function |
| --- | --- |
| `collapsible` | \block[ Make the section collapsible.  
**Default**: `False`
] |
| `alert` | \block[ Make an alert-box.  
**Default**: `False`

	**Possible Values**: 
	- `info`
	- `seccess`
	- `danger`
	- `warning`
	- `primary`
	- `secondary`
	- `light`
	- `dark`
] |


#### Card
Add card-style by adding `.card` to attribute list.  
(This will only work for bootstrap-based styles).

| Variable | Function |
| --- | --- |
| `width` | \block[ Adjust the relative width on the page.  
**Default**: `0` (maximal)
] |
| `subtitle` | \block[ Add a subtitle to the card.  
**Default**: `""` (Overwrite with a string.)
] |
| `cardheader` | \block[ Card-styled header.  
**Default**: `False`
] |
| `plain` | \block[ Plain card style.  
**Default**: `False`
] |


