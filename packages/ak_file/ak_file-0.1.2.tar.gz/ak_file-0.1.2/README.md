<!--- Heading --->
<div align="center">
  <img src="assets/banner.png" alt="banner" width="auto" height="auto" />
  <h1>ak-file</h1>
  <p>
    A base module to manipulate files and folders
  </p>
<h4>
    <a href="https://github.com/rpakishore/ak-file/">View Demo</a>
  <span> · </span>
    <a href="https://github.com/rpakishore/ak-file">Documentation</a>
  <span> · </span>
    <a href="https://github.com/rpakishore/ak-file/issues/">Report Bug</a>
  <span> · </span>
    <a href="https://github.com/rpakishore/ak-file/issues/">Request Feature</a>
  </h4>
</div>
<br />

[![tests](https://github.com/rpakishore/ak-file/actions/workflows/test.yml/badge.svg)](https://github.com/rpakishore/ak-file/actions/workflows/test.yml)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/rpakishore/ak-file)
![GitHub last commit](https://img.shields.io/github/last-commit/rpakishore/ak-file)
<!-- Table of Contents -->
<h2>Table of Contents</h2>

- [1. About the Project](#1-about-the-project)
  - [1.1. Features](#11-features)
- [2. Getting Started](#2-getting-started)
  - [2.1. Dependencies](#21-dependencies)
  - [2.2. Installation](#22-installation)
- [3. Usage](#3-usage)
- [4. License](#4-license)
- [5. Contact](#5-contact)
- [6. Acknowledgements](#6-acknowledgements)

<!-- About the Project -->
## 1. About the Project

A base project to simplify file manipulation

<!-- Features -->
### 1.1. Features

- Can sanitize filename based on windows limitaions
- Can search for and return files with specified filenames

<!-- Getting Started -->
## 2. Getting Started

### 2.1. Dependencies

The repo comes pre-compiled with all dependencies. Needs Python 3.11+

<!-- Installation -->
### 2.2. Installation

Install from pypi

```bash
pip install ak_file
```

<!-- Usage -->
## 3. Usage


```python
import ak_file
file = ak_file.File("<path/to/file>")

file.exists()

file.properties()

# To sanitize filename
from ak_file import sanitizer
sanitizer.sanitize("Dirty_windows_file_name.ext")

# Obfuscate/Unobfuscate filename with simple char shift
sanitizer.obfuscate('Filename to obfuscate') #'WzCvErDvqKFqFswLJtrKv'
sanitizer.obfuscate('Filename to obfuscate') #'Filename to obfuscate'

# To search for files with extension
from ak_file import search
search.by_extension(folder_path="Folder\path", extension="py", search_subdir=True)
```

<!-- License -->
## 4. License

See LICENSE for more information.

<!-- Contact -->
## 5. Contact

Arun Kishore - [@rpakishore](mailto:pypi@rpakishore.co.in)

Project Link: [https://github.com/rpakishore/ak-file](https://github.com/rpakishore/ak-file)


<!-- Acknowledgments -->
## 6. Acknowledgements

- [Awesome README Template](https://github.com/Louis3797/awesome-readme-template/blob/main/README-WITHOUT-EMOJI.md)
- [Shields.io](https://shields.io/)