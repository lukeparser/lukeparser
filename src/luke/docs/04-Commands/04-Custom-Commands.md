{theme=documentation}

\include{"../include.md"}

\title{"Custom Commands" " "}


With *luke*, it is possible to define custom commands directly in its own markdown dialect.


**Math-Commads**  
```latex
\newcommand{mc2}[$mc^2$]
\newcommand{Emc2}[$$E = mc^2$$]
This command can be used in a math setting: $( E = \mc2)$  
This command can also be used directly in markdown text. This is inline: \mc2  
The type of math-mode in the definition defines the inline text-style. This is a block: \Emc2
```
\Output[
\newcommand{mc2}[$mc^2$]
\newcommand{Emc2}[$$E = mc^2$$]
This command can be used in a math setting: $( E = \mc2)$  
This command can also be used directly in markdown text. This is inline: \mc2  
The type of math-mode in the definition defines the inline text-style. This is a block: \Emc2
]


**More Complicated Example**
```latex
\newcommand{blub var1 var2 attr1=42 attr2=43}[
**Param1**:  
%{arg0}% 

**Param2**:  
%{arg1}% 
]

\blub{test=42 var1_val var2=var2_val}[
    **arg0**: this is a text %{var2}% %{test}% %{attr2}%
][
    *arg1*
]
```
\Output[
\newcommand{blub var1 var2 attr1=42 attr2=43}[
**Param1**:  
%{arg0}% 

**Param2**:  
%{arg1}% 
]

\blub{test=42 var1_val var2=var2_val}[
    **arg0**: this is a text %{var2}% %{test}% %{attr2}%
][
    *arg1*
]
]


/*
## Variable From File
test.md:
{bla=[\include{"test.md"}]}

%{bla}%

``` {replace={FILE=%{bla}%}}
FILE
```

$$
\bla
$$
*/
