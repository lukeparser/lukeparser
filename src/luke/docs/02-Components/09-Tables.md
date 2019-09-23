{theme=documentation}

\include{"../include.md"}

\title{Tables "& Card Tables"}



## Tables
Tables aren't part of the core Markdown spec, but they are part of GFM and *Lukeparser* supports them as well.

**Note** how the special Characters `$` and `|` are escaped.

```
The colons indicate the alignment of the columns.

| Tables        | Are           | Cool |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | \$1600 |
| col 2 is      | centered      |   \$12 |
| zebra stripes | are neat      |    \$1 |

There must be at least 3 dashes separating each header cell.  
The outer pipes (\|) are optional, and you don't need to make the raw Markdown line up prettily. You can also use inline Markdown.

Markdown | Less | Pretty
--- | --- | ---
*Still* | `renders` | **nicely**
1 | 2 | 3
```
\Output[
The colons indicate the alignment of the columns.

| Tables        | Are           | Cool |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | \$1600 |
| col 2 is      | centered      |   \$12 |
| zebra stripes | are neat      |    \$1 |

There must be at least 3 dashes separating each header cell.  
The outer pipes (\|) are optional, and you don't need to make the raw Markdown line up prettily. You can also use inline Markdown.

Markdown | Less | Pretty
--- | --- | ---
*Still* | `renders` | **nicely**
1 | 2 | 3
]


### Card Tables
Card tables can be used for page-headers or as a structure help.  
As this is more of a gimmick, we moved this to our [extra section](../03-Extra-Components/01-Card-Tables.md).

### Attributes

#### Internal Attribute Names {.collapsible}

| Variable | Function |
| --- | --- |
| `type` | `table` |
| `alignment` | A list of the column alignments. |
| `content` | A doubly nested list of table-rows and columns. |


