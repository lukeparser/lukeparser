import argparse
import json
import warnings
import os

from luke.views.html import html
from luke.parser.markdown import MLList


class Preprocessing(object):
    """
    A class which preprocesses and nests a given structure into a tree.
    """

    # extract [i+1:j] and insert into froms content
    # ignore also first and last hard break when collapsing
    def collapse(blocks, i, j, removefirsthardbreak=True):
        # get index of start element
        i2 = 1 if len(blocks) > i+1 and isinstance(blocks[i+1], dict) and removefirsthardbreak and blocks[i+1]["type"] == "hard break" else 0

        # get index of end element
        j2 = 1 if isinstance(blocks[j-1], dict) and blocks[j-1]["type"] == "hard break" else 0

        sub_blocks = blocks[i+1+i2:j-j2]
        blocks = blocks[:i+1] + blocks[j:]
        return blocks, sub_blocks

    # collapse the content-lists
    def collapseContent(blocks, i, j):
        blocks, sub_blocks = Preprocessing.collapse(blocks, i, j)
        return blocks, sub_blocks

    # find first occurence of fn(blocks[i])==True
    #   (including or excluding hard breaks)
    def findNext(blocks, i, fn, withHardBreak=False):
        if withHardBreak:
            j = i+1 # look ahead
            while j < len(blocks) \
                    and not (blocks[j]["type"] == "hard break" and fn(blocks[j+1])) \
                    and not fn(blocks[j]):
                j += 1
            return j

        else:
            j = i+1 # look ahead
            while j < len(blocks) and not fn(blocks[j]):
                j += 1
            return j

    # find first occurence of fn(blocks[i])==True
    #   (if predecessor is hard break, return that)
    def findWhile(blocks, i, fn, withHardBreak=False, withNewLine=True):
        if withHardBreak:
            j = i + 1  # look ahead
            while j < len(blocks) and (
                        (j < len(blocks)-1 and blocks[j]["type"] == "hard break" and fn(blocks[j+1]))
                        or blocks[j]["type"] == "new line"
                        or fn(blocks[j])
                    ):
                j += 1
            return j

        else:
            j = i + 1  # look ahead
            while j < len(blocks) and isinstance(blocks[j],dict) and (blocks[j]["type"] == "new line" or fn(blocks[j])):
                j += 1
            return j

    # def _resetIndent(self):
    #     self.indentList = []
    #     self.indentStr = ""

    # def _popIndent(self):
    #     self.indentList = self.indentList[:-1]
    #     self.indentStr = "".join(self.indentList)

    # change whitespace-string to level
    def whitespaceToLevel(self, whitespace, indentStr, indentList):
        # first, get the whitespace only
        whitespace = whitespace[:len(whitespace)-len(whitespace.lstrip())]

        if whitespace == "":
            indentList = []
            indentStr = ""
            return 0, indentStr, indentList

        # check if indendation is equal
        if whitespace == indentStr:
            return len(indentList), indentStr, indentList

        # check if indendation decreases or is equal
        for i in range(len(indentList)-1,0,-1):
            if whitespace == "".join(indentList[:i]):
                indentList = indentList[:i]
                indentStr = "".join(indentList)
                return i, indentStr, indentList

        # check if indendation increases
        if whitespace.find(indentStr) == 0:
            whitespace = whitespace[len(indentStr):]
            indentList.append(whitespace)
            indentStr += whitespace
            return len(indentList), indentStr, indentList

        # check if indendation decreases (case: 2 indent followed by 1 indent
        if indentStr.find(whitespace) == 0:
            l = len(indentStr) - len(whitespace)
            indentStr = whitespace
            for i in range(len(indentList)-1,0,-1):
                indent = indentList.pop()
                if len(indent) == l:
                    break
                elif len(indent) > l:
                    indentList.append(indent[:-l])
                else:
                    l -= len(indent)
            # TODO indentList needed?
            return len(indentList), indentStr, indentList

        # error in indentation
        raise ValueError("Wrong indentation: "+indentStr.replace("\t","\\t").replace(" ","\\s")+" followed by "+whitespace.replace("\t","\\t").replace(" ","\\s")+"\n")


    def nest_blocks(self, blocks, currentLevel=0, indentStr="", indentList=None):
        if not isinstance(blocks,list):
            return blocks
        if indentList is None:
            indentList = []

        # change whitespace to level
        i = 0
        while i < len(blocks):
            current = blocks[i]

            if isinstance(current, dict) and "level" in current and isinstance(current["level"],str):
                try:
                    current["level"], indentStr, indentList = self.whitespaceToLevel(current["level"], indentStr, indentList)
                except ValueError:
                    # try to resolve wrong indendation: assume indendation is same as last one
                    current["level"], indentStr, indentList = len(indentList), current["level"], [current["level"]]
            i += 1

        # by iterating list, nest into tree
        i = 0  # current index
        while i < len(blocks):
            current = blocks[i]

            if not isinstance(current, list) and not isinstance(current,dict):
                pass

            # all isinstance-ifs are used for content-lists
            elif isinstance(current, list):
                current = [self.nest_blocks(c, currentLevel, indentStr, indentList[:]) if isinstance(c,list) else self.nest_blocks([c], currentLevel, indentStr, indentList[:]) for c in current]

            # has no type (just in case)
            elif "type" not in current:
                pass

            # merge attributes with softbreak into next block
            elif i<len(blocks)-1 \
                    and isinstance(blocks[i], dict) \
                    and blocks[i]["type"] == "attributes" \
                    and blocks[i+1]["type"] != "hard break":

                blocks[i].pop("type")
                blocks[i+1].update(blocks[i])
                # remove the attribute-block
                blocks = blocks[:i] + blocks[i+1:]
                i -= 1  # check this index again

            # if found section, merge everything into section until section with same or higher level is found
            # (sections have highest priority of all)
            elif current["type"] == "section":

                # merge sections that are not seperated by newlines
                j = Preprocessing.findWhile(blocks, i, withHardBreak=False, fn=lambda next:
                        isinstance(next,dict) and "level" in next and next["level"] == current["level"] and "h-level" in next  and next["h-level"] == current["h-level"])

                # collapse all elements in between
                blocks, next_lines = Preprocessing.collapse(blocks, i, j)
                new_title = [current["title"]]
                for n in next_lines:
                        new_title.append({"type": "new line"})
                        new_title.append(n["title"])
                current["title"] = new_title

                # find next occurence of section of same or lower level
                j = Preprocessing.findNext(blocks, i, lambda next:
                        isinstance(next,dict) and next["type"] == "section" and next["level"] <= current["level"] and next["h-level"] <= current["h-level"])

                # check if next element is ending section
                # ignore ending element in this case
                if j < len(blocks) and "end" in blocks[j] and blocks[j]["end"]:
                    blocks = blocks[:j] + blocks[j+1:]

                # arguments, if are last real objects belong to outer scope
                found_attribute = j
                for j_test in range(j-1,i,-1):
                    if isinstance(blocks[j_test],dict) and blocks[j_test]["type"] == "attributes":
                        found_attribute = j_test
                    elif isinstance(blocks[j_test],dict) and blocks[j_test]["type"] != "hard break":
                        break
                j = found_attribute

                # collapse all elements in between
                blocks, current["content"] = Preprocessing.collapse(blocks, i, j)
                current["content"] = MLList(self.nest_blocks(current["content"], currentLevel, indentStr, indentList[:]))

            # if found element with level. nest all elements with higher level 
            elif "level" in current and "content" in current:

                # skip all occurences of lists of lower level
                j = Preprocessing.findWhile(blocks, i, withHardBreak=True, fn=lambda next:
                        isinstance(next,dict) and "level" in next and next["level"] > current["level"])

                # collapse all elements in between
                blocks, new_content = Preprocessing.collapse(blocks, i, j, removefirsthardbreak=False)
                current["content"] = [current["content"]] + new_content
                current["content"] = MLList(self.nest_blocks(current["content"], currentLevel, indentStr, indentList[:]))

            # if found element with content. nest all elements with same type
            elif "content" in current and current["type"] not in ["image"]:

                # skip all occurences of lists of lower level
                j = Preprocessing.findWhile(blocks, i, withHardBreak=False, fn=lambda next:
                        isinstance(next,dict) and "content" in next and next["type"] == current["type"])

                # collapse all elements in between
                blocks, new_content = Preprocessing.collapse(blocks, i, j)
                current["content"] = current["content"] + [ci for c in new_content for ci in (c["content"] if "content" in c else [c])]
                current["content"] = MLList(self.nest_blocks(current["content"], currentLevel, indentStr, indentList[:]))

            # nest all image captions
            elif "content" in current and current["type"] == "image":
                current["content"] = self.nest_blocks(current["content"])

            # nest all arguments
            if isinstance(current,dict) and "type" in current and current["type"] == "command" and "arguments" in current:
                for arg in range(len(current["arguments"])):
                    current["arguments"][arg] = self.nest_blocks(current["arguments"][arg], currentLevel, indentStr, indentList[:])

            # nest all arguments
            if isinstance(current,dict) and "type" in current and current["type"] == "attributes":
                for k,val in current.items():
                    if isinstance(val,list):
                        current[k] = self.nest_blocks(val)

            i += 1

        # remove empty input, if at start or end
        if len(blocks) > 0 and isinstance(blocks[0], str) and blocks[0].strip() == "":
            blocks = blocks[1:]
        if len(blocks) > 1 and isinstance(blocks[-1], str) and blocks[-1].strip() == "":
            blocks = blocks[:-1]
        # return blocks

        # as now, all levels are nested, we can merge by the semantics
        i = 0  # current index
        while i < len(blocks):
            current = blocks[i]

            if not isinstance(current, dict):
                pass

            # has no type (just in case)
            elif "type" not in current:
                pass

            # single-line command
            elif current["type"] == "paragraph" and len(current["content"]) == 1 and len(current["content"][0]) == 1 and isinstance(current["content"][0][0], dict) and current["content"][0][0]["type"] in ["latex_command","command"]:
                blocks[i] = current["content"][0][0]

            # collapse all lists (same level at this point) into one
            elif current["type"] in ["olist", "ulist", "indent", "quote"]:
                islist = current["type"] in ["olist","ulist"]

                # skip all occurences of elements that are indended with the same level (except lists)
                j = Preprocessing.findWhile(blocks, i, withHardBreak=not islist and current["level"] > 0, fn=lambda next:
                    isinstance(next,dict) and next["type"] == current["type"])

                if j-i>=1:

                    # collapse all elements in between
                    blocks, new_content = Preprocessing.collapse(blocks, i, j, removefirsthardbreak=islist)
                    # if the next element is of the same type, use only its content list
                    new_content2 = [c for b in new_content for c in ([b["content"]] if "content" in b else [b])]
                    current["content"] = [current["content"]] + new_content2
                    current["content"] = MLList([(MLList(c)  if isinstance(c,list) else c) for c in current["content"]]) # TODO can be done better

                    # append symbols, if exists
                    if "symbols" in current:
                        new_symbols = [b["symbols"][0] if "symbols" in b else None for b in new_content]
                        current["symbols"] = current["symbols"] + new_symbols

            # remove indendation at currentLevel
            elif current["type"] == "indent" and current["level"] == currentLevel+1:
                blocks = blocks[:i] + current["content"] + blocks[i+1:]


            i += 1

        return blocks

    def convertScope(self, blocks, scope=None):
        if not isinstance(blocks,list):
            return scope, blocks

        # scope of all definitions in same level (yes, also after descending)
        if scope is None:
            scope = {
                # 'footnote': {},
                # 'note': {},
                # 'image': {},
                # 'link': {},
                # 'variable': {},
                # 'latex_command': {},
            }

        # remove an element 
        #   - remove one hardbreak, if it was surrounded by two
        #   - preceding hardbreak, if element is at the end
        #   - subsequent hardbreak, if element is at the begining
        def removeWithHardBreaks(blocks, i):
            if i > 0 \
                    and isinstance(blocks[i-1], dict) \
                    and blocks[i-1]["type"] == "hard break" \
                    and i < len(blocks)-1 \
                    and isinstance(blocks[i+1], dict) \
                    and blocks[i+1]["type"] == "hard break":
                blocks = blocks[:i] + blocks[i+2:]
            elif i == 0 \
                    and len(blocks) > 1\
                    and isinstance(blocks[i+1], dict) \
                    and blocks[i+1]["type"] == "hard break":
                blocks = blocks[i+2:]
            elif i > 0 \
                    and i == len(blocks) \
                    and isinstance(blocks[i-1], dict)\
                    and blocks[i-1]["type"] == "hard break":
                blocks = blocks[:i-1]
            else:
                blocks = blocks[:i] + blocks[i+1:]
            return blocks

        i = 0
        while i < len(blocks):
            item = blocks[i]

            if isinstance(item, list):
                list_scope, blocks[i] = self.convertScope(blocks[i])

                # update scope
                for subscope in list_scope.keys():
                    if subscope not in scope:
                        scope[subscope] = list_scope[subscope]
                    else:
                        scope[subscope].update(list_scope[subscope])
                i += 1

            elif not isinstance(item, dict):
                i += 1

            # extract href definitios
            elif item["type"].endswith("_definition"):
                subscope = item["type"][:-11]
                if subscope not in scope:
                    scope[subscope] = {}
                scope[subscope][item["ref"]] = item
                blocks = removeWithHardBreaks(blocks, i)

            # remove hardbreaks from free attributes
            elif item["type"] == "attributes" and i < len(blocks)-1 and blocks[i+1]["type"] == "hard break":
                blocks = blocks[:i+1] + blocks[i+2:]

            # traverse content, if exists
            elif "content" in item:
                item_scope, item["content"] = self.convertScope(item["content"])
                if item["type"] == "paragraph":

                    # update scope
                    for subscope in item_scope.keys():
                        if subscope not in scope:
                            scope[subscope] = item_scope[subscope]
                        else:
                            scope[subscope].update(item_scope[subscope])
                else:
                    item["scope"] = item_scope


                i += 1
            elif "arguments" in item:
                item_scope, item["arguments"] = self.convertScope(item["arguments"])
                item["scope"] = item_scope

                i += 1
            else:
                i += 1

        return scope, blocks 

    def run(self, blocks, filename, reduceIndentation=0):
        relpath = filename

        # block list -> tree
        tree = self.nest_blocks(blocks)

        filename_full = os.path.basename(filename)
        basepath = os.path.dirname(filename)
        filename, fileext = os.path.splitext(filename_full)

        # merge href-definitions in subsection (prepend to tree)
        scope, tree = self.convertScope(tree, scope={
            "variable": {
                    "fileext": fileext,
                    "filename": filename,
                    "filename_full": filename_full,
                    "relative_path":relpath,
                    "absolute_path": os.path.abspath(relpath),
                    "basepath": basepath,
                    "assets": "./"
                    }
        })

        return {"type": "document", "content": tree, "scope": scope}
