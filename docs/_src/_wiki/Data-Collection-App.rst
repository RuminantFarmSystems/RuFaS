Data Collection App
===================

Introduction
------------

The Data Collection App (DCA) is a user-friendly interface for creating
RuFaS inputs.

.. _what--why:

What & Why
----------

The DCA is built with a framework called
`JSON-Editor <https://github.com/json-editor/json-editor>`__, which
creates simple, easy-to-use HTML (webpage) interfaces for entering data
and saving it in JSON form. The DCA was built to make it easier for
users to create RuFaS inputs without having to work with raw JSON files.

How
---

Creating the DCA Schemas
~~~~~~~~~~~~~~~~~~~~~~~~

If you have never worked with the DCA before on your computer, the first
step to using it is creating the schema. There is a dedicated :doc:`Task manager tasks <Task-Manager>`
for this: ``"DATA_COLLECTION_APP_UPDATE"``. This task has already been
written up in ``input/data/tasks/dca_update_task.json``. Change the
``"path"`` in the ``"tasks"`` blob of ``task_manager_metadata.json``
from ``"input/data/tasks/default_task.json"`` to
``"input/data/tasks/dca_update_task.json"`` then run RuFaS the usual way
e.g. ``python main.py``. The DCA should now be ready to roll on your
computer!

*Note*: each time the metadata properties are updated, the DCA should
also be updated. If it isn't, it is possible that inputs created with
the DCA will not be valid. So it is a good idea to run the DCA update
task regularly, even if there are schemas already generated on your
computer.

Using the DCA
~~~~~~~~~~~~~

To start using the DCA, navigate to the RuFaS directory with your
computer's file explorer. Click on the directory titled
``DataCollectionApp``, then ``index.html``.

.. figure:: /_static/dca1.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview

After clicking on ``index.html``, a webpage should pop-up in your
default browser. Now you're all set to start using the DCA!

.. figure:: /_static/dca2.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview

To start working on a new input file, click the "+ Data Entry" button.
Then select which type of input you would like to create from the
drop-down. After all the data has been entered, click the blue "Save
Results" button to save all your data entries as JSON files.

.. figure:: /_static/dca3.png
   :alt: RuFaS Overview - GG
   :align: center
   :name: rufas overview

*Note*: when "Save Results" is clicked, there maybe a warning from the
browser warning that there are multiple files to be downloaded. This is
expected and normal, so it is safe to allow multiple files to be
downloaded in this case.

Now you have a new set of RuFaS JSON input files in your Downloads!

Working on the DCA
~~~~~~~~~~~~~~~~~~

This section is aimed at developers working on the DCA.

When the schemas of the DCA are updated, ``index.html`` is also updated
to ensure that the new schemas are found properly. Check out the
``data_collection_app_updater.py`` in ``RUFAS/`` to see the exact
mechanics of this. It is important to know that the ``template`` text
file is grabbed, the schemas added to it, and then is used to completely
overwrite ``index.html``. Because of this, it is **VERY IMPORTANT** that
both ``template`` and ``index.html`` are changed when the scripts in the
DCA are modified or added to, besides the ones which are updated
automatically when schema are generated. If ``index.html`` has any
changes or improvements that are not duplicated exactly in ``template``,
they will be lost as soon as the DCA update task is run.

*Tip*: ChatGPT knows about JSON-Editor, so it can especially helpful to
include that you are working with this framework when prompting it.
