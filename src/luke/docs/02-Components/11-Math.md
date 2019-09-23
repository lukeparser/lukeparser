{theme=documentation}

\include{"../include.md"}

\title{"Math Mode" "& Custom LaTeX Commands"}

{.alert}
**Note** that altough equations are displayed as block-elements. The Markdown-Syntax allows them to appear inline. That is why the attribute has to be given in the same line. Otherwise the attribute would be given to the paragraph it is in.


## Plain Markdown

```
In markdown, you can just include LaTeX-Math into your Document, like this: $E = mc^2$.

More complex formulas can be defined as block-elements:

$$
	\mathcal{A}(u) = \int_\Omega\left( 1+ |\nabla u|^2\right)^{1/2} dx_1 \dots dx_n.
$$
Text surrounds these nicely.
```
\Output[
In markdown, you can just include LaTeX-Math into your Document, like this: $E = mc^2$.

More complex formulas can be defined as block-elements:

$$
	\mathcal{A}(u) = \int_\Omega\left( 1+ |\nabla u|^2\right)^{1/2} dx_1 \dots dx_n.
$$
Text surrounds these nicely.
]

## Equation Numbers and References
Equation Numbers are easy, just give the equation an id.  

```
{#anid}$$
	\mathcal{A}(u) = \int_\Omega\left( 1+ |\nabla u|^2\right)^{1/2} dx_1 \dots dx_n.
$$

Later, reference the equation $\ref{anid}$ using the given id.
```
\Output[
{#anid}$$
	\mathcal{A}(u) = \int_\Omega\left( 1+ |\nabla u|^2\right)^{1/2} dx_1 \dots dx_n.
$$

Later, reference the equation $\ref{anid}$ using the given id.
]

You can also overwrite the equation number:
```
{#anid2 eqnum=surf}$$
	\mathcal{A}(u) = \int_\Omega\left( 1+ |\nabla u|^2\right)^{1/2} dx_1 \dots dx_n.
$$
```
\Output[
{#anid2 eqnum=surf}$$
	\mathcal{A}(u) = \int_\Omega\left( 1+ |\nabla u|^2\right)^{1/2} dx_1 \dots dx_n.
$$
]

## Custom LaTeX Commands
You can define custom LaTeX-Commands using the following syntax.  

**Note** the syntax differs from LaTeX command-definition.  
(See the [Commands Section](12-Commands.md) for more Information.)
```
\newcommand{cmdname}[$Some \LaTeX-Content$]
```
or
```
\newcommand{cmdname}[$
	Some LaTeX-Content
$]
```

### Arguments
Arguments can be referenced using `%{argNUM}%`.  
For example, we define a blue-text command.
```
\newcommand{bluetext}[$
	\textbf{%{arg0}%}. \color{blue}{\text{%{arg1}%}}. \text{Other \LaTeX-Content follows.}
$]

$$
	\bluetext{This is bold}{This is Blue}
$$
```
\Output[
\newcommand{bluetext}[$
	\textbf{%{arg0}%}. \color{blue}{\text{%{arg1}%}}. \text{Other \LaTeX-Content follows.}
$]

$$
	\bluetext{This is bold}{This is Blue}
$$
]


## Attributes

### Internal Attribute Names {.collapsible}

| Variable | Function |
| --- | --- |
| `type` | `math_block` or `math_inline` |
| `id` | Id for the math-equation. (Only for `math_block`) |
| `verbatim` | List of LaTeX-Commands. |


