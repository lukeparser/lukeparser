#include <pybind11/pybind11.h>
#include "antlr4-runtime.h"
#include "MarkdownLexer.h"
#include "MarkdownParser.h"
#include "MarkdownParserBaseListener.h"
#include <iostream>


using namespace antlr4;

class TreeShapeListener : public MarkdownParserBaseListener {
public:
    void enterBlock(MarkdownParser::BlockContext * /*ctx*/) override {
    // void enterMarkdown(ParserRuleContext *ctx) override {
        std::cout << "markdown" << std::endl;
        // Do something when entering the key rule.
    }
};


int main(int argc, const char* argv[]) {
  std::cout << argv[1] << std::endl;
  std::ifstream stream;
  stream.open(argv[1]);
  ANTLRInputStream input(stream);
  MarkdownLexer lexer(&input);
  CommonTokenStream tokens(&lexer);
  MarkdownParser parser(&tokens);

  tree::ParseTree *tree = parser.markdown();
  TreeShapeListener listener;
  tree::ParseTreeWalker::DEFAULT.walk(&listener, tree);

  return 0;
}




/*
int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(glue, m) {
    m.def("add", &add);

    #ifdef VERSION_INFO
        m.attr("__version__") = VERSION_INFO;
    #else
        m.attr("__version__") = "dev";
    #endif
}
*/
