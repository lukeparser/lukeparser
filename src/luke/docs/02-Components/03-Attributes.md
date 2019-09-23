{theme=documentation}

\include{"../include.md"}

\title{Attributes "Extending Elements"}

Variables is a mechanism to save anything in a variable.  
The same mechanism can be used to extend the functionality of Elements.


{.alert}
What comes next is a bit technical. If you want, you can skip this section first.


## More Definition Styles
Variable list can be formulated in many different ways -- for your convenience.  
Choose any of the styles below, or mix them.

**JSON**
```json
{
	"variable1": "word",
	"variable2": "A whole sentence.",
	"variable3": 42.3
}
```

**Luke Style**
```json
{
	variable1=word
	variable2="A whole sentence."
	variable3=42.3
}
```


**No Style** -- just Scramble
```json
{
	variable1:word,
	"variable2":"A whole sentence."
	variable3=42.3
}
```


## Shortcuts
We have multiple shortcusts for variable lists:
- `.variablename` is equivalent to `variablename=True` or `variablename=T`
- `!variablename` is equivalent to `variablename=False` or `variablename=F`
- `#reference` is equivalent to `id=reference`
- `.reference` will be passed directly to class attribute of the html-element, if given directly to the element.


## Concatenation
To concatenate a string to an existing variable use the following syntax.
```
{variable1=word}

{variable1={"more " %{variable1}% s}}

%{variable1}%
```
\Output[
{variable1=word}

{variable1={"more " %{variable1}% s}}

%{variable1}%
]



## Attributes
For more variability, any element can change behaviour by specified attributes.
If you use a variable list right before an element, then the variable are given as arguments to the element.

For instance, prepending a paragraph using the attribute `alert`.
```markdown
Outside important paragraph.

{.alert}
This is a very important paragraph.  
This text is still in the paragraph.

Outside important paragraph.
```
\Output[
Outside important paragraph.

{.alert}
This is a very important paragraph.
This text is still in the paragraph.

Outside important paragraph.
]

**Note** that inline-elements, like images, need the attribute list to appear in the same line. 
(Otherwise you would target the paragraph).
Don't worry, we will note in the next sections how to add attributes to one or another element.
```markdown
Right before the element: {variable="abc"}![Subcaption](image.png) End of line.
```
\Output[
Right before the element: {variable="abc"}![Subcaption](image.png). End of line.
]



## Scopes
Instead of repeating an attribute for all elements, you can just define a variable with the same name.
```markdown
{variable="abc"}

[Subcaption 1](image1.png)

[Subcaption 2](image2.png)

[Subcaption 3](image3.png)
```

Is the same as.

```markdown
{variable="abc"}[Subcaption 1](image1.png)

{variable="abc"}[Subcaption 2](image2.png)

{variable="abc"}[Subcaption 3](image3.png)
```

What's so scopy about it? Well, variables live only in the scope they were defined in.
```markdown
Global Scope-Variable:
{global_var="defined"}

# Outer Scope
This variable lives only until next Section of same level.
{variable="outer"}

## Inner Scope
Works: %{global_var}%  
Works: %{variable}%  
{inner_var="abc"}

## Inner Scope
Works: %{global_var}%  
Works: %{variable}%  
// Does not exist: %{inner_var}%.


# Outer Scope
Works: %{global_var}%  
// Does not exist: %{variable}%.
// Does not exist: %{inner_var}%.
Global Scope-Variable:
```
\Output[
Global Scope-Variable:
{global_var="defined"}

# Outer Scope
This variable lives only until next Section of same level.
{variable="outer"}

## Inner Scope
Works: %{global_var}%  
Works: %{variable}%  
{inner_var="abc"}

## Inner Scope
Works: %{global_var}%  
Works: %{variable}%  
// Does not exist: %{inner_var}%.


# Outer Scope
Works: %{global_var}%  
// Does not exist: %{variable}%.
// Does not exist: %{inner_var}%.
]


## Nested Variables

To group things, you can also nest these definitions.
```json
{
	variable1="word"
	variablegroup={
		subvar1="this result"
		subvar2="that result"
	}
}

Call the variable using %{variablegroup.subvar1}% or %{variablegroup.subvar2}%.
```
\Output[
{
	variable1="word"
	variablegroup={
		subvar1="this result"
		subvar2="that result"
	}
}

Call the variable using %{variablegroup.subvar1}% or %{variablegroup.subvar2}%.
]
