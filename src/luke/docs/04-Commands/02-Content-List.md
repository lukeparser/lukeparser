{theme=documentation}

\include{"../include.md"}

\title{"Content List" " "}



## Basic Contentlist
The Contentlist-Command can be called anywhere in the document.

```latex
\contentlist(clear=False,maxdepth=-1)
```

**Useage**
```
{.section-counter}

**Content List**
# Level 1

## Level 2

### Level 3

## Level 2

## Level 2

### Level 3

# Level 1

---

**Content List**
\contentlist

**Content List with maximal depth**
\contentlist{maxdepth=2}
```
\Output[
{.section-counter}

\clearcounter
\contentlist{.create}

# Level 1

## Level 2

### Level 3

## Level 2

## Level 2

### Level 3

# Level 1

---

**Content List**
\contentlist

**Content List with maximal depth**
\contentlist{maxdepth=2}

]



### Clearing and Creating new Lists

**Clear the List**  
To clear the list until this particular moment, call
```
\contentlist{.clear}
```
(This command does not return anything.)

**Create a List in a Subelement**  
To create a new list that is seperated from the global list, call
```
\contentlist{.create}
```
(This command does not return anything.)



