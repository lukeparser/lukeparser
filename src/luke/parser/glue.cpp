#include <pybind11/pybind11.h>
#include "antlr4-runtime.h"
#include "MarkdownLexer.h"
#include "MarkdownParser.h"
#include "MarkdownParserBaseVisitor.h"
#include <iostream>
#include <any>


using namespace antlr4;

class PythonGlueVisitor : public MarkdownParserBaseVisitor  {
public:

  virtual antlrcpp::Any visitMarkdown(MarkdownParser::MarkdownContext *ctx) override {
      return 42;
      return "markdown";
    // return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitBlocks(MarkdownParser::BlocksContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitBr(MarkdownParser::BrContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitEmptyline(MarkdownParser::EmptylineContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitWs(MarkdownParser::WsContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitBlock(MarkdownParser::BlockContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitIndent_blocks(MarkdownParser::Indent_blocksContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitHeadline(MarkdownParser::HeadlineContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitUlist(MarkdownParser::UlistContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitUlist_elem(MarkdownParser::Ulist_elemContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitOlist(MarkdownParser::OlistContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitOlist_elem(MarkdownParser::Olist_elemContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitQuote(MarkdownParser::QuoteContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitQuote_elem(MarkdownParser::Quote_elemContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitText(MarkdownParser::TextContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitText_br(MarkdownParser::Text_brContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitInline_element(MarkdownParser::Inline_elementContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitString(MarkdownParser::StringContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitEmph(MarkdownParser::EmphContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitStrong(MarkdownParser::StrongContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitBold(MarkdownParser::BoldContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitItalic(MarkdownParser::ItalicContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitLink(MarkdownParser::LinkContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitImage(MarkdownParser::ImageContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitReference(MarkdownParser::ReferenceContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitUrl(MarkdownParser::UrlContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitInline_footnote(MarkdownParser::Inline_footnoteContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitPositional_footnote(MarkdownParser::Positional_footnoteContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitReferenc_footnote(MarkdownParser::Referenc_footnoteContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitRendered_image(MarkdownParser::Rendered_imageContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitHyperref_url(MarkdownParser::Hyperref_urlContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitHyperref_definition_url(MarkdownParser::Hyperref_definition_urlContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitHyperref_definition(MarkdownParser::Hyperref_definitionContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitCode_inline(MarkdownParser::Code_inlineContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitCode_block(MarkdownParser::Code_blockContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitTable(MarkdownParser::TableContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitTable_row(MarkdownParser::Table_rowContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitTable_separator_row(MarkdownParser::Table_separator_rowContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitTable_separator(MarkdownParser::Table_separatorContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitCmd(MarkdownParser::CmdContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitCmd_arg(MarkdownParser::Cmd_argContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitMath_inline(MarkdownParser::Math_inlineContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitMath_block(MarkdownParser::Math_blockContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitMath_text(MarkdownParser::Math_textContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitMath_cmd(MarkdownParser::Math_cmdContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitAttributes(MarkdownParser::AttributesContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitAttribute(MarkdownParser::AttributeContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitAttribute_name(MarkdownParser::Attribute_nameContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitAttribute_value(MarkdownParser::Attribute_valueContext *ctx) override {
    return visitChildren(ctx);
  }

  virtual antlrcpp::Any visitAttribute_blocks(MarkdownParser::Attribute_blocksContext *ctx) override {
    return visitChildren(ctx);
  }


};


auto parse() {
    const char *argv[] = {"test.md"};
  std::cout << argv[1] << std::endl;
  std::ifstream stream;
  stream.open(argv[1]);
  ANTLRInputStream input(stream);
  MarkdownLexer lexer(&input);
  CommonTokenStream tokens(&lexer);
  MarkdownParser parser(&tokens);

  tree::ParseTree *tree = parser.markdown();
  PythonGlueVisitor visitor;
  auto a = visitor.visit(tree);
  std::cout << int(a) << '\n';
  // std::cout << a.as<std::string>() << '\n';

  return 0;
}



int add(int i, int j) {
    return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(lukeparsermarkdown, m) {
    m.def("add", &add);

    #ifdef VERSION_INFO
        m.attr("__version__") = VERSION_INFO;
    #else
        m.attr("__version__") = "dev";
    #endif
}

int main(int argc, const char* argv[]) {}
