{theme=documentation}

\include{"../include.md"}

\title{Variables "Variables & Attributes"}

Sometimes you do not want to rewrite something several times, or you want to make it easy to change it in the future.
Well, we can just save it to a variable and print it later.



### Definition
To define a variable, just start a variable list with a `{`, list some variables and end the list with a `}`. You should see no output.  
Note, that the names `variable1`, `variable2` and `variable3` can be chosen freely.
```json
{variable1=word variable2="a whole sentence." variable3=42.3}
```
{variable1=word variable2="a whole sentence." variable3=42.3}


### Print
The list above stores the variables. To place them anywhere in your document, you either write the variable name in such curly brackets, `%{variable1}%` or prepend it with a backslash, `\variable1`.
```
Sometimes I forget a %{variable1}%.  
Sometimes I forget a \variable2.  
But most importantly, I do not forget the number %{variable3}%.   
I say it again **%{variable3}%**.
```
\Output[
Sometimes I forget a %{variable1}%.  
Sometimes I forget a \variable2.  
But most importantly, I do not forget the number %{variable3}%.   
I say it again **%{variable3}%**.
]

{.alert}
**There is no difference between the syntax `%{variable1}%` and `\variable1`.**  
As `\variable1` ends with no symbol it is not possible to write something like
`by\variable1s` (this would result in an error, as `variable1s` was not defined.  
Instead, you can use `by%{variable1}%s` to remove any unwanted spaces.  
(There are more such corner cases, in which the variable needs to be seperated clearly from its surroundings.)




### Save Markdown in a Variable
To define a variable to include markdown itself use the block-syntax `[ markdown ]`.
```
{markdown_var=[
This is **markdown**: www.google.de
]}

%{markdown_var}%
```
\Output[
{markdown_var=[
This is **markdown**: www.google.de
]}

%{markdown_var}%
]


## Save a Markdown File In A Variable
```
{bla=[\include{"test.md"}]}

%{bla}%
```
\Output[
{bla=[\include{"test.md"}]}

%{bla}%
]




### Template
This feature might come handy, if you also include variables inside these defined bloks.

Let's say, you want to include a list of upcoming movies, each entry designed in a specific way.  
*(Note: we will define the elements such as the box, links and text emphasis later, don't worry :) ).*

```
{.alert}
Check **Minuteman -- Lost in Time%** out!  
Coming soon to theaters *(27. July 2042)*  
[*Click this link to read more*](http://minuteman.time)

{.alert}
Check **The guy who never lived** out!  
Coming soon to theaters *(31. June 2022)*  
[*Click this link to read more*](http://namelessmovie.indie)

{.alert}
Check **Again, a drama lama** out!  
Coming soon to theaters *(3. May 2025)*  
[*Click this link to read more*](http://whatsthereasonforthisthing.hollywood)
```
\Output[
{.alert}
Check **Minuteman -- Lost in Time%** out!  
Coming soon to theaters *(27. July 2042)*  
[*Click this link to read more*](http://minuteman.time)

{.alert}
Check **The guy who never lived** out!  
Coming soon to theaters *(31. June 2022)*  
[*Click this link to read more*](http://namelessmovie.indie)

{.alert}
Check **Again, a drama lama** out!  
Coming soon to theaters *(3. May 2025)*  
[*Click this link to read more*](http://whatsthereasonforthisthing.hollywood)

]


This can be done much easier, with template-variables.

```
{movietext=[

{.alert}
Check **%{name}%** out!  
Soon coming to theaters *(%{releasedate}%)*  
[*Click this link to read more*](%{link}%)

]}

\movietext{name=Minuteman releasedate="27. July 2042" link="http://minuteman.time"}
\movietext{name="The guy who never lived" releasedate="31. June 2022" link="http://namelessmovie.indie"}
\movietext{name="Again, a drama lama" releasedate="3. May 2025" link="http://whatsthereasonforthisthing.hollywood"}
```
\Output[
{movietext=[

{.alert}
Check **%{name}%** out!  
Soon coming to theaters *(%{releasedate}%)*  
[*Click this link to read more*](%{link}%)

]}

\movietext{name=Minuteman releasedate="27. July 2042" link="http://minuteman.time"}
\movietext{name="The guy who never lived" releasedate="31. June 2022" link="http://namelessmovie.indie"}
\movietext{name="Again, a drama lama" releasedate="3. May 2025" link="http://whatsthereasonforthisthing.hollywood"}
]

{movietext=[

{.alert}
Check **%{name}%** out!  
Soon coming to theaters *(%{releasedate}%)*  
[*Click this link to read more*](%{link}%)

]}

or, depending on your style and preference, you can also use it like this

```
\for{list={
    {name=Minuteman releasedate="27. July 2042" link="http://minuteman.time"}
    {name="The guy who never lived" releasedate="31. June 2022" link="http://namelessmovie.indie"}
    {name="Again, a drama lama" releasedate="3. May 2025" link="http://whatsthereasonforthisthing.hollywood"}
}}[
\movietext
]
```
\Output[
\for{list={
    {name=Minuteman releasedate="27. July 2042" link="http://minuteman.time"}
    {name="The guy who never lived" releasedate="31. June 2022" link="http://namelessmovie.indie"}
    {name="Again, a drama lama" releasedate="3. May 2025" link="http://whatsthereasonforthisthing.hollywood"}
}}[
\movietext
]
]


{movietext=[

{.alert}
Check **%{name}%** out!  
Soon coming to theaters *(%{releasedate}%)*  
[*Click this link to read more*](%{link}%)

]}

