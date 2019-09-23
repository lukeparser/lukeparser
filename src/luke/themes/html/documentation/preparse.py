

class Preparse():

    def preparse(tree):

        # prepend default components
        prepend = [

            # left
            {"content": [ [ { "arguments": [ [ { "content": [ [ { "command": "listdocuments", "nargs": [], "nested": True, "type": "command", "walk_only_current_dir": True, "basepath": [{"command":"basepath","type":"placeholder"},'/../'] } ] ], "level": "\t", "type": "indent" } ] ], "command": "component", "nargs": [ "left" ], "type": "command" } ] ], "type": "paragraph" },

            # right
            { "content": [ [ { "arguments": [ [ { "content": [ [ { "command": "contentlist", "nargs": [], "nested": True, "type": "command" } ] ], "level": "\t", "type": "indent" } ] ], "command": "component", "nargs": [ "right" ], "type": "command" } ] ], "type": "paragraph" }
        ]


        tree["content"] = prepend + tree["content"]
        return tree
