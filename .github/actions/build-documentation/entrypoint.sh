#!/bin/sh -l

# install luke requirements
pip install -r requirements.txt

# parse documentation
python luke.py src/luke/docs/ -o . --resources-with-file -t documentation.html --cdn

# remove all markdown files
find docs -name "*.md" -delete;
