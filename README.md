# Luke, I'm Your Parser.
[![python-3 badge](https://img.shields.io/pypi/v/lukeparser)](https://pypi.org/project/lukeparser/)
[![python-3 badge](https://img.shields.io/pypi/pyversions/lukeparser)](https://pypi.org/project/lukeparser/)
[![wheel](https://img.shields.io/pypi/wheel/lukeparser)](https://github.com/lukeparser/lukeparser)
[![Build & Deploy](https://github.com/lukeparser/lukeparser/workflows/Build%20&%20Deploy/badge.svg)](https://github.com/lukeparser/lukeparser)

> The Style of Markdown with the Power of LaTeX.

Powered by blazing fast **Bison/Flex** and magnificent & extensible **Python3**.

<div align="center">
  <a href="http://lukeparser.github.io">
    <img width=650px src="https://lukeparser.github.io/assets/logo_wide.png">
  </a>
</div>



## Features
Did you ever missed these functions in Markdown?

- **variables and custom commands** in Markdown - in Math- and in Textmode?
- additional parameters for each component for more variation and control?
- **custom styles** - you can also use different styles in the same document
- the choice to **compile to LaTeX or HTML** - or both at the same time?
- **references across files**?
- a easy **searchable representation** of chapters, images, and other components of your documents
- **component nesting** using indentation, e.g. sections in lists
    - we use an automatic indentation-style detection (spaces or tabs)
- **Notes and Footnotes in a seperate file or part of your document**.
- **nested multiline comments**
- an inplace server for live parsing of markdown files as **a replacement for simple php**


## Getting Started

**Documentation**  
Read the [Documentation online.](https://lukeparser.github.io/lukeparser).

**Install** (Linux, Windows & OS X)
```sh
pip install lukeparser
```

**Start a live reload server anywhere**
```
luke --live
```

**Usage example**
```
luke file.md
```

_For more examples and usage, please see our docs._


## Contributing

1. Fork it (<https://github.com/lukeparser/lukeparser/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## License
Code: [![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg?style=flat-square)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)  
Language Definition: [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)  
© 2019 David Hartmann. With the exceptions noted below, this code is released under the GPL, version 2. This software carries no warranty of any kind. The language specification and the documentation, written in the *luke markdown dialect* are licensed under the MIT license.
