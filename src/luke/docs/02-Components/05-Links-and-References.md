{theme=documentation}

\include{"../include.md"}

\title{"Links" "& Hyperrefs"}



## Plain Markdown

There are multiple ways to create links.

```
[I'm an inline-style link](https://www.google.com)  
[I'm an inline-style link with title](https://www.google.com "Google's Homepage")  
[I'm a reference-style link][Arbitrary case-insensitive reference text]  
[I'm a relative reference to a repository file](../blob/master/LICENSE)  
[You can use numbers for reference-style link definitions][1]  

Or leave it empty and use the [link text itself].

URLs and URLs in angle brackets will automatically get turned into links.  
http://www.example.com or www.example.com

Some text to show that the reference links can follow later.

[arbitrary case-insensitive reference text]: https://www.mozilla.org
[1]: http://slashdot.org
[link text itself]: http://www.reddit.com
```
\Output[
	[I'm an inline-style link](https://www.google.com)  
	[I'm an inline-style link with title](https://www.google.com "Google's Homepage")  
	[I'm a reference-style link][Arbitrary case-insensitive reference text]  
	[I'm a relative reference to a repository file](../blob/master/LICENSE)  
	[You can use numbers for reference-style link definitions][1]  

	Or leave it empty and use the [link text itself].

	URLs and URLs in angle brackets will automatically get turned into links.  
	http://www.example.com or www.example.com

	Some text to show that the reference links can follow later.

	[arbitrary case-insensitive reference text]: https://www.mozilla.org
	[1]: http://slashdot.org
	[link text itself]: http://www.reddit.com
]


## Document References
Give any element an id-Attribute and reference it somewhere else in the same document.
```

# Heading with Id {#heading1}
Some text

...

Later in document:
As seen in a [previous Section](#heading1).

It is also possible to reference [sections within other documents](02-Variables.md#Attributes)
```
\Output[
# Heading with Id {#heading1}
Some text

...

Later in document:
As seen in a [previous section](#heading1).

It is also possible to reference [sections within other documents](02-Variables.md#Attributes)
]

## Predefined Attributes

### Internal Attribute Names {.collapsible}

| Variable | Function |
| --- | --- |
| `type` | `url` or `link` |
| `dest` | Hyperlink-Url |
| `ref` | Reference Name |
| `content` | Hyperlink-Text |
| `alt_text` | Alternative Text (Mouse-over Text) |
