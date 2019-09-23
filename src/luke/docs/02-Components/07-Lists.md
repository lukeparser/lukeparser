{theme=documentation}

\include{"../include.md"}

\title{Lists "Things need to be ordered."}



## Plain Markdown

```
1. First ordered list item
2. Another item
   * Unordered sub-list. 
1. Actual numbers don't matter, just that it's a number
   1. Ordered sub-list
4. And another item.

   You can have properly indented paragraphs within list items. Notice the blank line above, and the leading spaces (at least one, but we'll use three here to also align the raw Markdown).

   To have a line break without a paragraph, you will need to use two trailing spaces.⋅⋅
   Note that this line is separate, but within the same paragraph.⋅⋅
   (This is contrary to the typical GFM line break behaviour, where trailing spaces are not required.)

   ### Even Documents
   Even better, just intend a whole document, to make it appear as part of a list.

* Unordered list can use asterisks
- Or minuses
+ Or pluses
```
\Output[
1. First ordered list item
2. Another item
   * Unordered sub-list. 
1. Actual numbers don't matter, just that it's a number
   1. Ordered sub-list
4. And another item.

   You can have properly indented paragraphs within list items. Notice the blank line above, and the leading spaces (at least one, but we'll use three here to also align the raw Markdown).

   To have a line break without a paragraph, you will need to use two trailing spaces.⋅⋅
   Note that this line is separate, but within the same paragraph.⋅⋅
   (This is contrary to the typical GFM line break behaviour, where trailing spaces are not required.)

   ### Even Documents
   Even better, just intend a whole document, to make it appear as part of a list.

* Unordered list can use asterisks
- Or minuses
+ Or pluses
]


## Specify List-Symbol (for ordered lists)

### by Syntax {.collapsible}

Luke will check the first symbol of a connected list to specify the list-symbol.

**Decimal**
```
1. list element
2. list element
3. list element
```
\Output[
1. list element
2. list element
3. list element
]

**Decimal with leading zero**
```
01. list element
02. list element
03. list element
```
\Output[
01. list element
02. list element
03. list element
]


**lower Roman**
```
i. list element
ii. list element
iii. list element
```
\Output[
i. list element
ii. list element
iii. list element
]


**upper Roman**
```
I. list element
II. list element
III. list element
```
\Output[
I. list element
II. list element
III. list element
]



**lower Alpha**
```
a. list element
b. list element
c. list element
```
\Output[
a. list element
b. list element
c. list element
]



**upper Alpha**
```
A. list element
B. list element
C. list element
```
\Output[
A. list element
B. list element
C. list element
]


### by Attributes {.collapsible}
To overwrite automatic detection of list-symbols in the current scope, just overwrite the attribute-default.
```
{list-symbol=lower-alpha}


1. list element
1. list element
1. list element
```
\Output[
{list-symbol=lower-alpha}

1. list element
1. list element
1. list element
]

### Bold List-Symbols {.collapsible}
```
{.list-style-bold}
1. list element
1. list element
1. list element
```
\Output[
{.list-style-bold}
1. list element
1. list element
1. list element
]

## Specify List-Symbol (for unordered lists)

### by Syntax {.collapsible}

#### Symbol by depth (default)
Luke will change the symbol of a unordered list by analysing the depth of the list.

```
- list element
- list element
    - list element
    - list element
    - list element
        - list element
        - list element
            - list element
            - list element
            - list element
        - list element
        - list element
    - list element
    - list element
- list element
- list element
```
\Output[
- list element
- list element
    - list element
    - list element
    - list element
        - list element
        - list element
            - list element
            - list element
            - list element
        - list element
        - list element
    - list element
    - list element
- list element
- list element
]

#### Automatic Symbol detection
You can change that behaviour by overwriting the attribute `list-symbol`.
**Auto**
```
{list-symbol=auto}
```
(You can either specify this variable globally, or locally in the line before the list.)

{list-symbol=auto}

Again, the first symbol of a connected unordered list will specify the list-symbol of the list.

**Bullets**
```
* list element
* list element
* list element
```
\Output[
* list element
* list element
* list element
]

**Dashes**
```
- list element
- list element
- list element
```
\Output[
- list element
- list element
- list element
]


**Circles**
```
+ list element
+ list element
+ list element
```
\Output[
+ list element
+ list element
+ list element
]


### by Attributes {.collapsible}
To overwrite automatic detection of list-symbols in the current scope, just overwrite the attribute-default.

**Bullets**
```
{list-symbol=bullet}
- list element
- list element
- list element
```
\Output[
{list-symbol=bullet}
- list element
- list element
- list element
]


**Circles**
```
{list-symbol=circ}
- list element
- list element
- list element
```
\Output[
{list-symbol=circ}
- list element
- list element
- list element
]


**Line**
```
{list-symbol=line}
- list element
- list element
- list element
```
\Output[
{list-symbol=line}
- list element
- list element
- list element
]


### Icons as Symbols {.collapsible}
Luke supports the use of [openiconic](https://useiconic.com/open) symbols as list-symbols.
(Of course, the used theme needs to have openiconic installed for this to work!)

```
- list element
-[arrow-left] list element
-[arrow-right] list element
-[fork] list element
-[A] list element
- list element
```
\Output[
- list element
-[arrow-left] list element
-[arrow-right] list element
-[fork] list element
-[A] list element
- list element
]


## Todo-Lists
Luke can indeed produce todo-lists.  
If openiconic is enabled for your theme, luke supports their icons as todo-symbols as well.

```
-[] todo element
-[v] todo element
-[x] todo element
-[ ] todo element
-[?] todo element

{symbol-style=icon}
-[] todo element
-[v] todo element
-[x] todo element
-[ ] todo element
-[?] todo element
```
\Output[
-[] todo element
-[v] todo element
-[x] todo element
-[ ] todo element
-[?] todo element

{symbol-style=icon}
-[] todo element
-[v] todo element
-[x] todo element
-[ ] todo element
-[?] todo element
]


## Predefined Attributes

### Internal Attribute Names {.collapsible}

**For Ordered Lists**
| Variable | Function |
| --- | --- |
| `type` | `olist` |
| `list-symbol` | \block[ Specify the list-style.  
**Default**: `auto`

	**Possible Values**: 
	- `decimal`
	- `decimal-leading-zero`
	- `lower-roman`
	- `upper-roman`
	- `lower-alpha`
	- `upper-alpha`
] |
| `list-style-bold` | \block[ Specify the list-symbol thikness.  
**Default**: `False`
] |
| `content` | List of list elements. |

**For Unordered Lists**
| Variable | Function |
| --- | --- |
| `type` | `ulist` |
| `list-symbol` | \block[ Specify the list-style.  
**Default**: `auto-depth`

	**Possible Values**: 
	- `auto`
	- `bullet`
	- `circ`
	- `line`
] |
| `content` | List of list elements. |

