{theme=documentation}

\include{"../include.md"}

\title{"Control Flow" "Conditions and Loops"}


## Conditions

To evaluate any markdown copmonent or command based on a given condition use one of these conditional commands.

**If-Statement**
```
Current View: %{view}%

**Output**: \ifeq{%{view}% html}[
	IS HTML
][
	IS **NOT** HTML
]
```
\Output[
Current View: %{view}%

**Output**: \ifeq{%{view}% html}[
	IS HTML
][
	IS **NOT** HTML
]
]


**Negated Version**
```
Current View: %{view}%

**Output**: \ifneq{%{view}% latex}[
	IS **NOT** $\LaTeX$
][
	IS $\LaTeX$
]
```
\Output[
Current View: %{view}%

**Output**: \ifneq{%{view}% latex}[
	IS **NOT** $\LaTeX$
][
	IS $\LaTeX$
]
]



## Loops

**Simple Count Controlled Loop**
```
\for{10}[
	**current index**: %{i}% \n
]
```
\Output[
\for{10}[
	**current index**: %{i}% \n
]
]


**Define start, stop and step value**  
The for-Loop awaits the following Arguments
```
\for{to=0, start=0, step=1, index="i", list=[]}
```

To overwrite them use:  
(**Note** that the order of the arguments is only important if no key is given to the values)
```
**to overwrite in order:**  
\for{10 1 2}[
	**current index**: %{i}% \n
]

or 

**to overwrite by key:**  
\for{start=1 to=10 step=2}[
	**current index**: %{i}% \n
]
```
\Output[
**to overwrite in order:**  
\for{10 1 2}[
	**current index**: %{i}% \n
]

or 

**to overwrite by key:**  
\for{start=1 to=10 step=2}[
	**current index**: %{i}% \n
]
]


**Loop over a list**  
The for-loop allows to loop over a list of values.
```
\for{list={
	{name="Just another number" number=5} 
	{name="The truth" number=42} 
	{name="Just another number" number=20}
}}[
	%{name}%: $%{number}%$ \n
]
```
\Output[
\for{list={
	{name="Just another number" number=5} 
	{name="The truth" number=42} 
	{name="Just another number" number=20}
}}[
	%{name}%: $%{number}%$ \n
]
]


**Loops can be used with templates**  
```
{template=[
    The fabulous character of **%{name}%** *%{surname}%*
]}


\for{list={
    {name=James surname=Bond}
    {name=Rosa surname=Klebb}
    {name=Red  surname=Grant}
}}[
    \template \n
]
```
\Output[
{template=[
    The fabulous character of **%{name}%** *%{surname}%*
]}

\for{list={
    {name=James surname=Bond}
    {name=Rosa surname=Klebb}
    {name=Red  surname=Grant}
}}[
    ”\template“ **or** ”%{template}%“ \n
]
]
