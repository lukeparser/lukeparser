import os
from os.path import isdir, isfile, join, basename
import sys
import json

def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

# import luke
sys.path.insert(0, os.path.join("src"))
from luke.luke import parse_lang
from luke.parser.markdown import MarkdownParser
from luke.Preprocessing import Preprocessing
parser = MarkdownParser()
prep = Preprocessing()

root_dir = os.path.join("tests","parser")

# list all markdown files
testdirs = [join(root_dir, f) for f in os.listdir(root_dir) if isdir(join(root_dir, f))]
md_files = [join(d, f) for d in testdirs for f in os.listdir(d) if isfile(join(d, f)) and f.endswith(".md")]

def msg(msg,keylist):
    return "'"+msg+"' under the key '"+".".join(keylist)+"'."

def dictContains(src,expected,keylist=[]):
    assert isinstance(src,dict), msg("Is not a dict.",keylist)
    for key,val in expected.items():
        k = keylist+[key]
        assert key in src, msg("Does not contain the key.",k)
        if isinstance(val,dict):
            dictContains(src[key], val, k)
        elif isinstance(val,list):
            assert isinstance(src[key],list)
            for i,v in enumerate(val):
                assert src[key][i] == val[i], msg("Arrays do not match at index "+str(i)+".",k)
        else:
            assert type(src[key]) == type(val), msg("Not same types.",k)
            assert src[key] == val, msg("Not same value.",k)

def tfactory(file,json_file):
    def thetest():
        if not os.path.exists(json_file):
            assert False, "Missing result file"

        parser = MarkdownParser()
        prep = Preprocessing()
        res = parse_lang(parser,prep,file_path=file)

        with open(file, 'r') as f:
            md = f.read()
        with open(json_file, 'r') as f:
            expected = json.load(f)

        print("From:")
        print(md)
        print("Result:")
        print(json.dumps(res,indent=4,default=dumper))
        print("Expected:")
        print(json.dumps(expected,indent=4))
        dictContains(res,expected)

    return thetest


# check if all rules have a test
def test_allcasestested():
    for k in MarkdownParser.__dict__.keys():
        if not k.startswith("on_"):
            continue

        doc = MarkdownParser.__dict__[k].__doc__

        name, rules = doc.strip().split(":")
        name = name.strip()
        rules = [r.strip().split() for r in rules.split("|")]

        for rule in rules:
            if "error" in rule:
                continue
            if len(rule) == 0:
                rule = ["empty"]
            filename = os.path.join(root_dir,name,"-".join(rule))

            # (only for test writing)
            # create it
            # if not os.path.exists(os.path.join(root_dir,name)):
            #     os.makedirs(os.path.join(root_dir,name))
            # if not os.path.exists(filename+".md"):
            #     with open(filename+".md", 'w') as f:
            #         f.write(" ".join(rule))

            assert os.path.exists(filename+".md")

            # (only for test writing)
            if not os.path.exists(filename+".json"):
                parser = MarkdownParser()
                prep = Preprocessing()
                res = parse_lang(parser,prep,file_path=filename+".md")
                del res["scope"]
                with open(filename+".json", 'w') as f:
                    f.write(json.dumps(res,indent=4,default=dumper))
# test_allcasestested()

# walk all files and create a test
for file in md_files:
    rule = basename(os.path.dirname(file))
    testname = rule+"__"+basename(file).split(".")[0]
    json_file = file.replace(".md",".json")

    locals()["test_"+testname] = tfactory(file,json_file)
