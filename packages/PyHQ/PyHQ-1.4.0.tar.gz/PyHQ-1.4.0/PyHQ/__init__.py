# PyHQ - Init

''' This is the __init__.py file. '''

'''
Copyright 2023 Aniketh Chavare

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

# Imports
import webbrowser

# Variables
name = "PyHQ"
version = "1.4.0"
description = "PyHQ is an open-source, advanced, and multi-purpose Python package."
license = "Apache License 2.0"
author = "Aniketh Chavare"
author_email = "anikethchavare@outlook.com"
github_url = "https://github.com/anikethchavare/PyHQ"
pypi_url = "https://pypi.org/project/PyHQ"
docs_url = "https://anikethchavare.gitbook.io/pyhq"

# Function 1 - GitHub
def github():
    # Opening PyHQ's GitHub Repository
    try:
        webbrowser.open(github_url)
    except:
        raise Exception("An error occurred while opening the GitHub repository. Please try again.")

# Function 2 - PyPI
def pypi():
    # Opening PyHQ's PyPI Page
    try:
        webbrowser.open(pypi_url)
    except:
        raise Exception("An error occurred while opening the PyPI page. Please try again.")

# Function 3 - Docs
def docs():
    # Opening PyHQ's Docs
    try:
        webbrowser.open(docs_url)
    except:
        raise Exception("An error occurred while opening the docs. Please try again.")