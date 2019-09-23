{theme=documentation}

\include{"../include.md"}

\title{"Card Tables" "& Page Headers"}

Card tables can be used for page-headers or as a structure help.

{.alert}
These functions are intended to be used only together with the html view.

**How to use them**:
- each row can have a distinct number of cells. 
- each cell is prepended by a seperator, that defines the alignment of the cell.
- **note** that no header line ought to be given

```
{.card}
| :---                   | :---:           | ---:          |
| left aligned           | centered Text   | right aligned |
| :---                   | :---            |
| just two cells         | the second cell |
| each row is a new line |                 |
| :----------------------------------------------------------------------: |
| single cell                                                              |
| include any span **components**, like [links](www.github.com) or images. |
```
\Output[
{.card}
| :---                   | :---:           | ---:          |
| left aligned           | centered Text   | right aligned |
| :---                   | :---            |
| just two cells         | the second cell |
| each row is a new line |                 |
| :----------------------------------------------------------------------: |
| single cell                                                              |
| include any span **components**, like [links](www.github.com) or images. |
]


What follows are some examples for their useage.

### Structured Information Cards
```
{.card .withheader .cardheader}
| ----------------------- | ----------------------- | ----------------------- |
| Title                   | Title                   | Title                   |
|                         |                         |                         |
|                         |                         |                         |
| Information Text        | Information Text        | Information Text        |
|                         |                         |                         |
| **Subtitle:**           | **Subtitle:**           | **Subtitle:**           |
| Add some text.          | Add some text.          | Add some text.          |
|                         |                         |                         |
| **Subtitle:**           | **Subtitle:**           | **Subtitle:**           |
| Lists are also possible | Lists are also possible | Lists are also possible |
| - list element          | - list element          | - list element          |
| - list element          | - list element          | - list element          |
| ----------------------- | ----------------------- |
| Title                   | Title                   |
|                         |                         |
|                         |                         |
| Information Text        | Information Text        |
|                         |                         |
| **Subtitle:**           | **Subtitle:**           |
| Add some text.          | Add some text.          |
|                         |                         |
| **Subtitle:**           | **Subtitle:**           |
| Lists are also possible | Lists are also possible |
| - list element          | - list element          |
| - list element          | - list element          |
```
\Output[
{.card .withheader .cardheader}
| ----------------------- | ----------------------- | ----------------------- |
| Title                   | Title                   | Title                   |
|                         |                         |                         |
|                         |                         |                         |
| Information Text        | Information Text        | Information Text        |
|                         |                         |                         |
| **Subtitle:**           | **Subtitle:**           | **Subtitle:**           |
| Add some text.          | Add some text.          | Add some text.          |
|                         |                         |                         |
| **Subtitle:**           | **Subtitle:**           | **Subtitle:**           |
| Lists are also possible | Lists are also possible | Lists are also possible |
| - list element          | - list element          | - list element          |
| - list element          | - list element          | - list element          |
| ----------------------- | ----------------------- |
| Title                   | Title                   |
|                         |                         |
|                         |                         |
| Information Text        | Information Text        |
|                         |                         |
| **Subtitle:**           | **Subtitle:**           |
| Add some text.          | Add some text.          |
|                         |                         |
| **Subtitle:**           | **Subtitle:**           |
| Lists are also possible | Lists are also possible |
| - list element          | - list element          |
| - list element          | - list element          |
]

### Page Headers

This is a more complex example of a page-header:
- header cells use a custom style, they are started by the `.header`-Attribute.
- line-seperators are possible as well (`.line`-Attribute)

```
{.plain .card}
| ---------------------------------------------------------- | {.header} -----------------------------------: |
| ![](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/)                 | Lukeparser              | 
|                                                            | The power of LaTex with the Style of Markdown. |
|                                                            | **Isn't that nice?**                           |
| {.header .line} :-----------------------------------------------------------------------------------------: |
| You can also define a second Header                                                                         |
| With a Subtitle                                                                                             |
| As you can see, you can also define a second header spannig the full width.                                 |
| Just like that.                                                                                             |
| {.line} --------------------------------------------------------------------------------------------------- |

Then the page content starts...
```
\Output[
{.plain .card}
| ---------------------------------------------------------- | {.header} -----------------------------------: |
| ![](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/)                 | Lukeparser              | 
|                                                            | The power of LaTex with the Style of Markdown. |
|                                                            | **Isn't that nice?**                           |
| {.header .line} :-----------------------------------------------------------------------------------------: |
| You can also define a second Header                                                                         |
| With a Subtitle                                                                                             |
| As you can see, you can also define a second header spannig the full width.                                 |
| Just like that.                                                                                             |
| {.line} --------------------------------------------------------------------------------------------------- |

Then the page content starts...
]

