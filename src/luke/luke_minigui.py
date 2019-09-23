import sys
from PyQt5 import QtWidgets as qw
from PyQt5 import QtGui as qg
from PyQt5 import QtCore as qc
from io import StringIO
# from luke
from parser.markdown import Parser
from views.html import View
from Preprocessing import Preprocessing
#from luke.luke import *

class lukeMiniGUI(qw.QMainWindow):

    # spawn gui
    def spawn():
        app = qw.QApplication(sys.argv)
        gui = lukeMiniGUI()
        sys.exit(app.exec_())

    # Konstruktor
    def __init__(self):

        # Konstruktor von QWidget
        super().__init__()

        self.initParser(Parser, Preprocessing, View)
        self.init_main_window()
        self.show()

    def browseFiles(self):
        directory = qw.QFileDialog.getExistingDirectory(self, "Find Files", qc.QDir.currentPath())
        self.file_path.setText(directory)

    def init_main_window(self):
        self.setWindowTitle("Luke Minimal GUI")
        self.resize(qw.QDesktopWidget().availableGeometry(self).size() * 0.3);

        # vbox
        central = qw.QWidget()
        vbox = qw.QVBoxLayout()
        central.setLayout(vbox)
        self.setCentralWidget(central)

        # file chooser-btn
        btn_layout = qw.QHBoxLayout()
        label = qw.QLabel("Choose File")
        self.file_path = qw.QLineEdit()
        file_choose = qw.QPushButton("...")
        file_choose.clicked.connect(self.openClicked)
        btn_layout.addWidget(label)
        btn_layout.addWidget(self.file_path)
        btn_layout.addWidget(file_choose)
        vbox.addLayout(btn_layout)

        # compile-button
        compile_btn = qw.QPushButton("Compile")
        compile_btn.clicked.connect(self.on_click)
        vbox.addWidget(compile_btn)

        # show errors
        self.errors = qw.QTextBrowser()
        vbox.addWidget(self.errors)

    def openClicked(self):
        self.filename = qw.QFileDialog.getOpenFileName(self, 'Open File',".","(*.md)")[0]
        if self.filename:
            with open(self.filename,"rt") as file:
                self.file_path.setText(self.filename)

    def initParser(self, ParserClass, PreprocessingClass, ViewClass):
        self.parser = ParserClass(verbose=0, debug=0)
        self.prep = PreprocessingClass()
        self.view = ViewClass()

        # nicer print-function
        def report_syntax_error(msg, yytext, first_line, first_col, last_line, last_col):

            def color_white(txt):
                return "<font color=\"Black\">"+txt+"</font>"

            def color_red(txt):
                return "<font color=\"Red\">"+txt+"</font>"

            def color_blue(txt):
                return "<font color=\"Blue\">"+txt+"</font>"

            def make_bold(txt):
                return "<b>"+txt+"</b>"

            def reset_style(txt):
                return txt

            yytext = yytext.replace('\n', '\\n')
            args = (msg, yytext, first_line, first_col, last_line, last_col)
            err_msg = ''.join([
                color_red(make_bold("<br/>Error: ")), reset_style("%s"), "<br/>", "     ",
                color_blue("└ near "), make_bold('"%s"'),
                reset_style(color_blue(" (see ")),
                color_white(make_bold("line %d, pos %d to line %d, pos %d")),
                reset_style(color_blue(").<br/>")), reset_style('')
            ])
            raise self.parser.BisonSyntaxError(err_msg % args, list(args))
        self.parser.setSyntaxErrorReporting(report_syntax_error)

    def on_click(self):
        
        f = StringIO()
        sys.stdout = f
        sys.stderr = f

        # markdown to html (file)
        luke.parse_lang(self.parser, self.filename, verbose=False, newline="<br>")
        print("<br>")
        luke.apply_view(self.prep, self.view, self.filename, isDev=True, newline="<br>")
        print("<br>")
        print("✓")


        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        f.seek(0)
        # self.errors.setPlainText(f.read())
        self.errors.setHtml(f.read())
        # self.update()
        f.close()


if  __name__ == "__main__":
   lukeMiniGUI.spawn()
