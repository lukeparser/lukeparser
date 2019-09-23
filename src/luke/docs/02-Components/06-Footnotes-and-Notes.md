{theme=documentation}

\include{"../include.md"}

\title{"Footnotes" "& Notes"}

## Footnotes

There are multiple ways to create footnotes to reduce cluttering of your main document.

```
Just write some text and append any footnote-id.[^1]
(Note, that the id does not have to be a number.)

[^1]: This can be referenced anywhere in the document.
    It is also to include the definition from another file using include.  
    (See [custom commands](11-Commands.md) for that function.)

Inline footnotes are also possible.^[Just write the footnote right where it appears to.]

Sometimes it is nice to [mark all works]^[Like here in the inline footnote]. on which the footnote refers.  
Of course, instead of an inline footnote, you can use a [reference-id as well][^refid].

[^refid]: Like here in this definition.

Finally, to flush all footnotes of the current scope, call the command `\footnotes`.
Otherwise, all footnotes are collected and inserted at the end of the document.
\footnotes
```
\Output[
Just write some text and append any footnote-id.[^1]
(Note, that the id does not have to be a number.)

[^1]: This can be referenced anywhere in the document.
    It is also to include the definition from another file using include.  
    (See [custom commands](11-Commands.md) for that function.)

Inline footnotes are also possible.^[Just write the footnote right where it appears to.]

Sometimes it is nice to [mark all works]^[Like here in the inline footnote]. on which the footnote refers.  
Of course, instead of an inline footnote, you can use a [reference-id as well][^refid].

[^refid]: Like here in this definition.

Finally, to flush all footnotes of the current scope, call the command `\footnotes`.
Otherwise, all footnotes are collected and inserted at the end of the document.
\footnotes
]



## Notes
Notes are meant as very short remarks directly in the document.

```
Here's a sentence ![with a note]^[Well that is short.], you see?  
(Hover with the mouse over the marked text to read the note.)

Here's a sentence ![with a note][^ref], you see?  

[^ref]: Of course, like with footnotes, you can define the note seperately.
```
\Output[
Here's a sentence ![with a note]^[Well that is short.], you see?  
(Hover with the mouse over the marked text to read the note.)

Here's a sentence ![with a note][^ref], you see?  

[^ref]: Of course, like with footnotes, you can define the note seperately.
]


## Predefined Attributes

### Internal Attribute Names {.collapsible}

| Variable | Function |
| --- | --- |
| `type` | `footnote`, `footnote_inline`, `note` or `note_inline` |
| `ref` | Reference Name |
| `content` | Hyperlink-Text |
| `text` | Inline-Text |
