![Version](https://img.shields.io/static/v1?label=taggedcctbxsnipsplus&message=0.1&color=brightcolor)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)


# taggedcctbxsnipsplus
*cctbx* snippets that can be retrieved in Jupyter via tags and have a guide to sites to be edited in a comment block. 

This repo contains the *cctbxsnips* library for the Elyra-snippets extension for Jupyter Lab. 
Each snippet is in a separate javascript file with the `json` file extension. 
Clone this repo to the `~/Library/Jupyter/metadata/code-snippets` directory. 
The JSON files should be inside `~/code-snippets` and not inside `~/code-snippets/taggedcctbxsnipsplus`.

Each snippet file has a set of metadata. 
These data include a list of tags. 
The tags are used to find the snippet while editing a Jupyter notebook in JupyterLab.

A second copy of the code is included in a block comment. 
The tab stops are marked with dollar signs and placeholder values are inside curly braces.
The block commented code is meant to guide the user to sites that should be considered for editing.
## Update History

|Version      | Changes                                         | Date            |
|:-----------:|:-----------------------------------------------:|:---------------:|
| Version 0.1 |  Fixed typos in README.md                       | 2024 April 10    |


## Sources of funding

- NIH: R01 CA242845
- NIH: R01 AI088011
- NIH: P30 CA225520 (PI: R. Mannel)
- NIH P20GM103640 and P30GM145423 (PI: A. West)

