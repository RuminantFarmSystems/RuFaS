# Purpose

This folder contains all resources to generate the RuFaS model scientific documentation with quarto, 
including source code, references, media resources, etc.

# Structure

Below is a brief summary of how this folder is organized, broken into "Bare files" and "Folders":

##### Bare files: 

In addition to this `readme.md` file, the important files contained in this root folder are:

* _quarto.yml: the quarto project file. It configures how `quarto` generates the final documentation. Some 
important features to note are: defining which qmd files are used (`book:chapters`), defining the `.bib` file(s)
to use for the project (`bibliography`), defining which template files to use for the website (`format:html:css`) and 
for the PDF (`format:pdf:include-in-header`).

* index.qmd: the first qmd file that serves as the site index, which is the home page users will see when
opening the documentation website. 
<!-- Note: this file must be in the same directory as _quarto.yml to work properly. -->

* .gitignore: a directory-level gitignore file (separate from the main project `.gitignore`), which specifies which
paths should be excluded relative to this folder (e.g., ".quarto/" ignores the entire .quarto sub-folder).

##### Folders

* qmd: contains the `.qmd` quarto source code of the documentation, broken down into "chapter" files. 
Which chapters appear in the final documentation, and their order, are controlled by the quarto project `_quarto.yml`
file.

* resources: contains the materials referenced by the source code to be included in the final documentation, organized
into subfolders by data type:

  - `rufas.bib` (bare file): BibTex file from which in-text citations are pulled and the final bibliography is 
  constructed
  
  - table_data: files that contain the data to be presented in the documentation
  
  - images: pictures and other images referenced by the `.qmd` files.
  
  - templates: template files for this project (i.e., templates for rendering output, qmd templates, etc.)
  
  - references-audit: files relating to the reference audit <!-- Needed??? -->
  
* scripts: code files that do something useful related to the quarto documentation, examples include the 
code to audit the references (`quarto_audit.py`), scripts to render the documentation (`render-quarto.sh`), and
code to facilitate importing tables (`markdown_tables.py`<!-- placeholder -->)

* _book: the rendered output files created by `quarto`. Of particular interest are `index.hmtl` and `qmd/*.html`,
which is the website version of the documentation; as well as `rufas-scientific-documentation.pdf`, which is the 
PDF version. <!-- Note: this folder should ultimately be ignored by git, since we will use GitHub Actions to render
it from the source code on GitHub. -->

# Usage

To preview the documentation, ensure that [quarto is installed](https://quarto.org/docs/get-started/) and run the
following command from this directory:

```shell
quarto preview
```

That should open a web browser with the HTML version of the documentation.

To render the docs use:

```shell
quarto render
```

## Troubleshooting
<!-- TBD -->