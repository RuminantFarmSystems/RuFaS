=========================================================
Methods to Maintaining and Updating Scientific Documentation
=========================================================

Overview
========

This document aims to provide guidance for subject matter experts (**SME**) responsible for maintaining and updating the scientific documentation (**Sci Doc**) of Animal, Feed Storage, Crop and Soil, Manure, and eventually Economic modules of the Ruminant Farm Systems (**RuFaS**) model.

Context
=======

Currently, updates of scientific documentation occur on an as needed basis reporting the methodology that informs the RuFaS model. This section of the document provides an overview of the contents of these guidelines.

1. Define criteria for when the Sci Doc should be updated
2. Define when updates should be merged to dev vs. directly to test branches.
3. Provide specific step by step instructions for documentation workflow
4. Updated guidance for documentation updates that pertain to connections between modules or other details that fall outside of the purview of a specific module per se.
5. Provide guidance for review of updates
   - Outline steps to cross-check equation IDs, hyperlinks, and references.
6. Links and recommendations regarding document templates, helpful code structure (to format equations), and guidance to update indices that track relevant document abbreviations, labels, and references (including in text citations).

Please find more details and previously established guidelines at the link below:

`2025 Documentation Guide and Information <https://drive.google.com/drive/folders/1lTjAzxWSic-sUD239_yuo1Xt-_ABo0Kp>`__

Table of Contents
=================

`Overview <#overview>`__

`Context <#context>`__

`Table of Contents <#table-of-contents>`__

`Criteria to Update Documentation <#criteria-to-update-documentation>`__

`When is the Sci Doc Updated? <#when-is-the-sci-doc-updated?>`__

`Level of Documentation Update <#level-of-documentation-update>`__

`Major Updates <#major-updates>`__

`Minor Updates <#minor-updates>`__

`Patch Updates <#patch-updates>`__

`Workflow Model Update to Sci Doc Publication <#workflow-model-update-to-sci-doc-publication>`__

`Quick Step by Step Guidance <#quick-step-by-step-guidance>`__

`Step 1: Starting Sci Doc Updates <#step-1:-starting-sci-doc-updates>`__

`Document Updating Framework: Updating .tex Files <#document-updating-framework:-updating-.tex-files>`__

`Step 2: Begin Updating .tex files Branching <#step-2:-begin-updating-.tex-files-branching>`__

`Step 3: Files to Edit <#step-3:-files-to-edit>`__

`Step 4: Preview Changes <#step-4:-preview-changes>`__

`Step 5: Review: Cross-Checks and Committing Changes <#step-5:-review:-cross-checks-and-committing-changes>`__

`Review and Finalizing Documentation <#review-and-finalizing-documentation>`__

`Steps to Review of Content and Copy <#steps-to-review-of-content-and-copy>`__

`Cross-Check Linking, IDs, and Indices <#cross-check-linking,-ids,-and-indices>`__

`Step 6: Merging Branches and Closing PRs <#step-6:-merging-branches-and-closing-prs>`__

`Guidelines to Update Module Text: Conventions, Review Processes, and Documentation Structure <#guidelines-to-update-module-text:-conventions,-review-processes,-and-documentation-structure>`__

`Equations and IDs <#equations-and-ids>`__

`Figures and Tables <#figures-and-tables>`__

`References <#references>`__

`Gray Documentation Handling <#gray-documentation-handling>`__

`Formatting Gray Documents <#formatting-gray-documents>`__

Criteria to Update Documentation
================================

When to Update the Scientific Documentation?
----------------------------

Generally, changes to methodology are initiated after careful by request of the PML, particularly the Scientific Director, and immediately precede a model version update. This typically requires a review process before model updates are conducted and implemented. For more information about the decisionmaking process behind model version updating, please refer to (PROVIDE LINKING, maybe pr2840?)

All methodological updates should be clearly documented in the SciDoc and published for users at the time the model updates are implemented and merged into “test” to ensure accurate publication for users in real time with model version release.

Ideally these Sci Doc updates are merged to “dev” coinciding the model updates and their merge to “dev,” but the authors acknowledge that this is not always possible.

There are 3 major levels of scientific documentation updating defined as follows:

* Major Update
* Minor Update
* Patch

Their definition and how they should be conducted are outlined in more detail in the following section.

Level of Documentation Update
-----------------------------

The previous section outlined 3 levels of documentation update: Major, Minor, and Patch. Each of these vary in several ways

* Type of update (is this a change to current methods or an addition to the model?)
* Degree of change or update and time involved
* Timeline of creation and implementation or release

The following text may help the user determine what level of update they require and how to proceed.

Major Updates
~~~~~~~~~~~~~

These Sci Doc updates explain significant changes or additions to the model methodology and underlying structure. Larger, leadership directed changes and updates are determined based on guidelines outlined in other documentation. This can be reviewed here:(ADD LINKING maybe to pr2840?)

After model updates have been determined by PML and completed by SMEs and software engineers (**SWE**), an ***Issue*** or ***PR*** should be immediately initiated to update documentation to reflect these model changes. These should include details of equation changes, equation IDs, included references, figures and tables required, other images, and proposed hyperlinking.

All Sci Doc updates should be completed and merged to test at the time of model version merge to test and subsequently, released to Main simultaneously. Any model update may **not** be considered completed until Sci Doc updates have been initiated (by an ***Issue*** or ***PR***).

Minor Updates
~~~~~~~~~~~~~

These include smaller updates to either documentation format or actual methodology of the model. They may or may not rise to the level of a full model version update, but

* Add new features to the model or refine processes
* Alter the way users interact with inputs or outputs
* Format changes that are so great, they may change a users understanding of the SciDoc

Not all minor updates are the same. A minor update may need to wait until a model version update or it may require immediate implementation and release. A plan should be established prior to initiation of any changes to the Sci Doc.

Patch Updates
~~~~~~~~~~~~~

These are small updates that do **not** change outputs, inputs, interpretations, or represent any changes to model methodology. Patch changes may include

* Typos
* Hyperlink repairs
* Image updates (not new images, but fixing broken images)
* Template updates

Patch updates may require immediate merge to test and subsequent release. Discuss the options with the Scientific Director and formulate a timeline for release.

Workflow Model Update to Sci Doc Publication
============================================

At this point model changes have been conducted and may either be under review or already reviewed by SME and SWE. It is now time to update the documentation to reflect these changes.

Quick Step by Step Guidance
---------------------------

Step 1: Starting Sci Doc Updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a pull request (PR) for your Sci Doc update. Be sure that all updates are off of dev to keep Sci Doc versioning in line with model version updates.

* If you are not prepared to update the documentation at this time, create an Issue citing 1) the updates to the model, 2) relevant equations and proposed IDs, 3) all relevant reference material (include authors, article title, and year of publication).

Document Updating Framework: Updating .tex Files
------------------------------------------------

All updates can be made off of dev. Each module or “part,” including the gray documents, are maintained in individual ``.tex`` files (e.g. *animal.tex, manure.tex, crop_and_soil.tex, or feed_storage.tex*).

Step 2: Begin Updating .tex files Branching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a branch off of dev. New branch should include: name of the doc or module you are updating, your initials, and the date you are initiating the SciDoc changes (MMDD). For the purpose of this workflow, let’s call the example branch:

::

   upd_animal_bb1002

All relevant files are found in the menu of your integrated development environment (**IDE**).

::

   docs > scientific

Step 3: Files to Edit
~~~~~~~~~~~~~~~~~~~~~

All document formatting and \\usepackages are maintained in the *preamble.tex* file. If changes are required for headers and footers, table of contents of the full document (**TOC**), table designs, or installation of additional \\usepackages may be done in that file (**A**).

All updates to methodological text, contents of the tables, equations, figures or other content related material may be conducted in the .tex files with the simple module headers (**B**). Additionally, any new additions or updates to references may be done in the rufas.bib file.

1) **Full documentation format changes**

   * preamble.tex

2) **Module Methodology and Linking Updates**

   * animal.tex
   * manure.tex
   * crop_and_soil.tex
   * feed_storage.tex
   * rufas.bib
   * *gray_connectors.tex*
   * *…*

Compilation of .pdf documents are completed in separate files from those listed in sections **A** and **B**. These files are responsible for compiling the preamble.tex, relevant module .tex file, and formatting of each module to a single downloadable file. Each module has its own such document. The file “main.tex” generates the entire SciDoc complete with TOCs, Figure and Table indices, and references. No changes should be made to any of these documents (**C**) without prior discussion with the Scientific Director.

3) **Compilation Documents**

   * main.tex
   * animalmoddoc.tex
   * manuremoddoc.tex
   * cropandsoilmoddoc.tex
   * feedstoragemoddoc.tex
   * grayconnectmoddoc.tex
   * …

Step 4: Preview Changes
~~~~~~~~~~~~~~~~~~~~~~~

Compilation and preview of .pdf documents should occur automatically. All compilation occurs from the list in part (**C**) outlined in the previous step. These .tex files go to compile individual modules into .pdfs from their respective files in part (**B**). The full document is compiled from the main.tex file and should be considered as the preview of the version that will be made available in finalization.

Step 5: Review: Cross-Checks and Committing Changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Review and Finalizing Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At this point, all updates to documentation are ready for review and publishing. Again, the following should already be complete:

- [x] PR for model updates has been reviewed by a SME and SWE.
- [x] This should have triggered either a second PR to initiate Sci Doc updates
      (Remember, if a PR is not created immediately, an Issue with relevant information needed should be created).
- [x] PR for Sci Doc updates is initiated and a branch created off of the dev branch (unless otherwise discussed with Scientific Director and the Director of Software Engineering).
- [x] Appropriate .tex files have been updated with relevant changes. This includes, but is not limited to:
- Equations
- Figures, Tables, Images
- Labels and hyperlinking
- Reference material
- Updated indices (Equation ID, Images, Labels, References, Acronyms etc.)
- [x] Reviewers tagged in the Sci Doc PR

The following sections will begin from this point and continue to outline in more detail the processes of review of content and a detailed checklist to ensure that all coding and automation is correct.

Steps to Review of Content and Copy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Two reviewers are responsible for checking that the content of the updates correctly describe the change in methodology or updates to the model.

   1. One of these reviewers may be the SME that wrote the document.
   2. Both reviewers can be SMEs if needed.

2. Create the .html and generate a .pdf to allow for detailed inspection of formatting and check that all text and formulas are readable.

   1. Check for spelling and grammatical errors.
   2. Check Equation formatting.
   3. Review reference tags and ensure they are correct.

3. Cross-Check Linking, IDs, and Indices (see next section).
4. Scientific Director review and approval

Cross-Check Linking, IDs, and Indices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following checklist should be copied and pasted into the Sci Doc PR and checked off as each item is completed. A properly formatted checklist for GitHub can be found here: `Cross-Check List <https://docs.google.com/document/d/1Oz4Bb8NHNN08KT2hKfDLm9pIegneWDonb-jGTHveDo8/edit?tab=t.0>`__. Copy and paste directly into your Sci Doc PR.

List of formatting checks to complete before finalizing document updates:

- [ ] Generate the html to begin. (This list should be repeated with the pdf).
- [ ] Confirm the text make sense and accurately represent the changes made to the model
- [ ] Check that the TOC of the main.tex file is updating correctly in the full document.
      Remember that \\subsubsection is not included in the TOC
- [ ] Check that the TOC of the individual module is updating correctly.
      Remember that \\subsubsection is not included in the TOC
      *For the remainder of the checklist, if it does not apply, skip to the next step.*
- [ ] Check that all internal links use appropriate \\hyperref{}{} and should connect to the appropriate \\label{}. Make sure that there is only one \\label{}.
- [ ] If a new \\label{} was created for the update, ensure that it is added to the index.
- [ ] Check that external links are still appropriate
- [ ] Check the equation IDs correctly labelled and formatted appropriately.
- [ ] If a new equation was added, check that the index was updated.
- [ ] Check in-text citations. Are they referencing the correct publication? Do they link to the appropriate reference table?
- [ ] If a new reference was added, check that the index was updated.
- [ ] Repeat these steps with the pdf

Step 6: Merging Branches and Closing PRs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the review process has been completed by one or more SMEs, merge and close the Sci Doc PR. If the update is considered “major” and part of an official version update, merge your branch to dev until version release.

If this update is considered a “patch” and has been previously discussed with the Scientific Director, merge directly to test.

Guidelines to Update Module Text: Conventions, Review Processes, and Documentation Structure
=============================================================================================

`Original Doc of Conventions and Guidelines <https://docs.google.com/document/d/1e5gM7fuT06iQYDKvwUAB-jVaLjw3iZizXAdSnOEDco0/edit?tab=t.0>`__

Prior to updating documentation, model updates should be approved, reviewed, completed, and a second PR initiated. Two reviewers are required (ideally 1 SME and 1 SWE) for any PR that addresses updates to the model. The same system should be used for PRs that address any SciDoc updates.

For our purposes, scientific documentation is a detailed description of the underlying biological processes that need to be simulated and the document should be in outline and/or short bullet point form rather than length text. The purpose of the document is to serve as documentation for the model and is aimed at model users and reviewers. Below are some recommendations for what to include and how to format the documentation files.

1. Each \\section should align with a **process** or **method** that occurs in the model. There is no hard rule for what processes should make a section but some rules of thumb to think about would be:

   - If you think it is big enough to be its own section, it probably is
   - If it has its own .py file, it’s big enough to be its own section.
   - If it has more than 3 equations, maybe break it up into separate sections

2. The beginning of each section should include a ***brief***, high-level description of how the real life process is being modeled in RuFaS (how is reality translated to RuFality)

   - Where applicable, include references to the original works where this approach was documented in the scientific literature in this intro section

3. The rest of the section should be dedicated to providing a detailed description of the method. Be as brief as possible while including enough detail that someone could replicate the method without the code.
4. All parameters required to execute the functions described in each section should be clearly defined and indicated at the beginning of the section

   - The origins of **parameter inputs** for each function should be clearly defined as a **user input, model constant, or a variable** that is updated by the simulation engine.
   - If the parameter is a variable that is updated by the simulation engine the part of the model that updates it should be identified
   - Where **applicable variable bounds** should be included with minimal assumptions about what is understood to be a reasonable value

5. Where applicable, a **list of outputs** should also be provided.
6. All **required equations should be explicitly defined** and numbered

Equations and IDs
=================

`Index of Values <https://docs.google.com/spreadsheets/d/1qZtqzS8rXm85ITXiXKdWlyRCV0-i_vhOqkHOKJB6boQ/edit?gid=0#gid=0>`__
`Current Framework <https://docs.google.com/document/d/1K-7Eab4tx-LuGKMg3kD5rw5698mP5oMhVZLdX-8HL0c/edit?tab=t.0>`__

Insert Here

* Equation identification should consist of at least 3 ID values separated by periods.
  * The first ID value indicates the domain in which the equation belongs and should include two capital characters. The current values for this are:

    * AN - Animal
      * MN - Manure
      * SC- Soil and Crop
      * FS - Feed Storage
      * EN - Energy
      * EC - Economics
      * EM - Emissions

    * The second ID value indicates the sub-domain and should be used for high-level sub-sections and sub-modules within each domain and should be a 3 character abbreviation that is somewhat intuitive. A list of the Domains and their associated sub-domains are located later in this document.

      * If you do not see a subdomain that aligns with your work or you would like to propose a new name, make an GitHub issue and work through it with the appropriate team.

    * The fourth ID value is the number of equations required for that process and will be integers (1, 2, 3,...)
    * For example SC.ERO.4 would be the fourth equation in the erosion section of the the soil/crop module.

* If an equation is in the code, it should be detailed in the scientific documentation and vice versa– changes to either should warrant a change in the other following the next update.
* Try your best to match variable names between the code and the documentation. This helps immensely with readability. In the case of a subscript, use an underscore.

  * Variable names should be meaningful to someone who is not an expert in the field. For example:

    * *k* is often used to describe rate constants. Instead of defining a parameter as *k*\_*methane* to describe the rate of methane emissions from manure. Name the parameter manure_methane_emiss_rate (or something similar). Be creative! Think about what would make the most sense to your fellow team members and the person in your position 5 years from now

* The order in which processes are detailed in the scientific documentation should match the order in which they are executed in the code, and section names should match the names of the classes that contain the code described. You should be able to read the pseudocode and trace its implementation side by side without jumping around.

Figures and Tables
==================

* Figures and tables that are included should be appropriately sized and formatted to be legible. Refer to the templates available in the next section.
* All figures and tables should include a caption that describes the contents. Like all peer reviewed, published texts, captions must be detailed and be able to ‘stand alone’ in the document.
* All figures and tables should be properly documented and added to the index for tracking.

References
==========

* Many of RuFaS reference materials are already stored in the rufas.bib file found in *resources*. Check to see if the citation you want to use is available. If so, add your in text citation with a \\parencite{**appropriate_tag_name**} or \\cite{**appropriate_tag_name**}
* All new or updated reference material should be formatted to be automatically input into the scientific document. This way it can be hyperlinked and reviewed.
* If adding new reference material, be sure to add it to the index for tracking purposes.

Gray Documentation Handling
===========================

“Gray Documents” (**Gray Doc**) describe methods that apply to more than one module. One example of a Gray Doc is a “Connector Document” (**Connect Doc**), which explain how two or more modules rely on each other. Such documents, Gray Docs, belong in their own part of Sci Docs (separate from other module parts) because they do not neatly fit into a single module (Animal, Feed Storage, Soil and Crop, or Manure).

These Gray Docs may also describe formulas or unique scenarios that RuFaS is capable of executing, but may require more in depth understanding of inputs or additional steps. If you are unsure where to put some documentation that you are preparing, you are likely creating a Gray Doc. If there are still questions, be sure to discuss with the Scientific Director.

All Gray Docs should be added to the final part of the Sci Doc,“*Gray Documents and Module Connections*.” This is located after all 4 modules, but before “*References”* and “*Abbreviations*.”

Formatting Gray Documents
-------------------------

Given the nature of gray documentation and the flexibility of such texts, it is difficult to provide formatting recommendations. However, below is a similar overview of document structure as was provided in the previous “Guidelines” section. Adjustments have been made to example titles to better fit the needs of Gray Docs.

Note that it is important to add a \\label to every \\section header to allow hyperlinking within modules. It is recommended that hyperlinks be added immediately to the relevant text. All section labels should be indexed appropriately.

Insertion of Figures, Tables, Images, and Equations follow the same structure as normal modules as they are outlined in the previous section. Feel free to refer to those available code lines and templates to support the creation of your Gray Doc. Be sure to read them carefully and amend them as necessary to fit the needs of your text.

Upon completion (writing, review, and compilation) of your Gray Doc, be sure to download a .pdf and save to the SharePoint files (title it “G” for Gray Doc, abbreviated section title, and the date of update; e.g. G_AnimManConnect_MMDDYY).