Scientific Documentation
==========================

The scientific manual describes the model's equations, assumptions,
inputs, and scientific references. Use it to understand the processes
behind a simulation and to assess whether they fit your study.

Read the manual
-----------------

:download:`Download the scientific documentation (PDF) <../../scientific/main.pdf>`.

The manual covers these connected parts of the farm model:

* **Animal:** herd structure, growth, reproduction, nutrition, milk
  production, and animal emissions.
* **Manure:** manure handling, processing, storage, and associated
  emissions.
* **Crop and soil:** crop growth, field management, soil water, and
  nutrient cycling.
* **Feed storage:** feed inventories, storage processes, and their
  connection to animal feeding.

The PDF is a compiled snapshot. Check the release or commit used for
your analysis against the manual and its source; the source may include
changes made after the PDF was built. See :doc:`Known-Limitations` for
model scope and interpretation considerations.

Find related documentation
----------------------------

* :doc:`onboarding` introduces the modules and running the example model.
* :doc:`Data-Origins` explains where input data come from.
* :doc:`Input-Manager` describes input files and their validation.
* :doc:`Code reference <../_code/modules>` documents the implementation.
* :doc:`Release notes <_release_notes/index>` describe released changes.

Contribute scientific documentation
-------------------------------------

The LaTeX sources are in
`docs/scientific <https://github.com/RuminantFarmSystems/RuFaS/tree/dev/docs/scientific>`_,
with ``main.tex`` as the entry point. The
`Build scientific PDF workflow <https://github.com/RuminantFarmSystems/RuFaS/actions/workflows/build-scientific-docs.yml>`_
compiles the manual and uploads a ``scientific-pdf`` artifact. See
:doc:`Contributing-to-RuFaS` for participation and review guidance, and
:doc:`Branching-Strategy-in-RuFaS` for the scientific documentation branch
workflow.
