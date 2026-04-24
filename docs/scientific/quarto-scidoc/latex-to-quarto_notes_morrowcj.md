## Introduction

This documents contains my notes following my process of migrating a section of the scientific documentation from 
LaTeX (.tex) to quarto (.qmd). I with the "RuFaS Bodyweight and Growth" subsection of "Animal-level Process and 
Management" in the animal.tex file.
My contributions were done on a new branch (`animal-growth-quarto`) off of the main scidoc conversion branch 
(`quarto_sci_doc_updates_0318`). This was to avoid conflicts with the other team members concurrently working on the
scidoc transitions.

## Procedure

I took the following steps to convert the selected section of documentation:

* started by creating main heading and all subheadings for the Animal-level Process section `animal.qmd`
* then, copied all latex code for the subsection (between `\subsection{RuFaS Bodyweight and Growth}` and 
`\subsection{Animal Reproduction} `) and pasted it into the corresponding subsection in the qmd file. I also 
added the markdown comment "TODO" to all remaining subsections, to indicate that they remain incomplete
* removed the code blocks around all main text sections, adding line breaks to prevent the need for horizontal
scrolling while editing. My editor has a linewidth guide set for 120 characters, so I kept all lines within that
length. Note linebreaks in markdown are not treated as paragraph breaks. Instead, empty lines indicate a paragraph 
break.
* Paragraph titles within `\paragraph{}` were replaced by bolding the text (e.g., **Introduction**), as were text
within `\textbf{}`. 
* citations were converted via quarto conventions (e.g., `\textcite{Li2023}` became `@Li2023`).
* tables with python... TBD