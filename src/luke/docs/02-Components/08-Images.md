{theme=documentation}

\include{"../include.md"}

\title{Images "Show it!"}

{.alert}
Note, that Luke differs in Images slightly from classical markdown.  
We swapped the caption text and the alt-text for a more consistent syntax.

## Images

```
Inline-style: 
![Caption Text](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/)
![Caption Text](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "(optional\) Logo Title Text 1")
(Note the `\)` for the optional Alt-text.)

Reference-style: 
![Reference-Style Caption Text][logo]

![logo]: https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "Logo Title Text 2"
```
\Output[
Inline-style: 
![Caption Text](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/)
![Caption Text](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "(optional\) Logo Title Text 1")
(Note the `\)` for the optional Alt-text.)

Reference-style: 
![Reference-Style Caption Text][logo]

![logo]: https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "Logo Title Text 2"
]


### Captions
Captions can contain much more, than just some words.
```
![
The caption can span over multiple lines, and include a whole document itself.

Like Math ($\LaTeX$) or any other Component.

](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "Logo Title Text 1")
```
\Output[
![
The caption can span over multiple lines, and include a whole document itself.

Like Math ($\LaTeX$) or any other Component.

](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "Logo Title Text 1")
]


## Inline Images
Images can come as a block (see above) or as inline elements. To make an image inline, omit any content.
```
Text before image
![](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "Logo Title Text 1")
Text after image
```
\Output[
Text before image
![](https://avatars2.githubusercontent.com/u/47249302?s=200&v=4/ "Logo Title Text 1")
Text after image
]



## Predefined Attributes

### Always
| Variable | Function |
| --- | --- |
| `width` | \block[ Adjust width of the image.  
**Default**: `0`

	**Possible Values**: 
	- `0` to `100` (percent)

	**Sub-Types for HTML**:
	- `width_lg` (large screens, uses value of `width` by default)
	- `width_md` (middle sized screens, uses value of `width` by default)
	- `width_sm` (small screens, uses value of `width` by default)
	- `width_xs` (mobile screens, uses value of `width` by default)
] |

#### Internal Attribute Names {.collapsible}

| Variable | Function |
| --- | --- |
| `type` | `image` |
| `alt-text` | The optional alternative text. |
| `content` | The caption text. |
| `dest` | The image destination. |

### HTML-View
| Variable | Function |
| --- | --- |
| `plain` | \block[ Remove any image borders.  
**Default**: `False`
] |

#### Card
Add card-style by adding `.card` to attribute list.  
(This will only work for bootstrap-based styles).

