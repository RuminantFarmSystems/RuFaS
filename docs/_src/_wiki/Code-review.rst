Code Review
===========
Code review is as important as developing the code. In this wiki, we go
over the details of the code review process in RuFaS.

Before code review begins
-------------------------

The author(s) responsible for making the code **reviewable**.
Reviewability is achieved by ensuring that:

- Making a PR means that the code is ready to be merged as-is. A PR has
  to have any temporary and test files and pieces of code removed, and a
  clean and ready-to-merge submission is needed.
- Author(s) has correctly identified which part of the codebase needs
  modification. This typically means the author has properly linked the
  Github issue the PR is addressing.
- Author(s) have fully tested their changes and documented how they have
  tested the code under ``Test Plan`` section in the PR description.
- The code review is NOT mixed with a design review. If the change is
  large, `its idea and design have to be reviewed and agreed
  upon <https://github.com/RuminantFarmSystems/MASM/wiki/How-to-write-a-design-doc%3F>`__;
  before developing the code and submitting it for review.
- The code that is being submitted for review is adequately sized, it is
  not too small nor too large. As a general rule of thumb, anything
  larger than 200 lines of code is considered large.
- All functions that are modified or added have accompanying unit tests.
- All functions that are modified or added have accompanying NumPy style
  docstrings.
- All functions that are modified or added are type annotated.
- The code passes all linting checks in alignment with the Flake8 style
  (review linting practices in RuFaS
  :doc:here <Using-Flake8>`).
- The pull request has a reasonably written description following the
  what-why-how framework. Clearly state what are you changing/adding,
  why is this important/needed, and explain how it works.
- More is NOT better. Everyone's time is important, avoid writing
  essay-long descriptions. Instead of stating *"in this PR, we increase
  the molecular movements in water particles by increasing the thermal
  energy to achieve phase transition from liquid to gas"*, simply say
  *"we boil water here"*.
- Communicate with the reviewer; let them know that you need their
  review. Give them enough time.
- Everyone is busy, don't be shy to remind the reviewer that you need
  them if your code is still pending after a few days.
- Functions are reasonably sized, complex/large functions are bad, so
  avoid them!
- Don't repeat yourself, if there is a part of code that is being
  repeated, figure out a way to avoid the repetition.
- Comments are bad and should be avoided. The code has to be clean
  enough to explain itself. In exceptional cases, it might be acceptable
  to have comments explaining why a certain approach is chosen (a
  comment that explains what the code is doing, rather than why is it
  the way it is, is not acceptable.
- The branch was rebased onto the main before submitting the code for
  review.
- Unused files are not being submitted for review.
- The PR is passing all Github Actions - testing, linting, formatting,
  et al.
- Add an entry to the changelog describing the changes made in the PR.
  Then look at the changelog in the "Files Changed" tab of the PR to
  make sure that *no other changes* were made to the changelog besides
  the addition of your entry.

Reviewing the code
------------------

Code review practices:

- Set aside a block of time to do the code review. Everyone is
  different, find out what is the optimal time window for you, in which
  you can stay focused.
- Take a rest when you feel tired.
- Don't mix code review with other works; avoid parallel processing.
  Focus on reviewing only one submission at a time.
- Read the Pull Request description. Make sure the code is doing the
  same thing that the description says.
- If you are unable to review, let the author(s) know.
- Make sure all modified or added functions are type annotated and have
  accompanying unit tests and docstrings.
- Make sure the test suite is comprehensive and does not have any holes.
- Make sure the test suite encompasses normal operations, edge cases,
  and invalid inputs.
- Make sure all actions and signals are "go". (As of writing this, we
  have signals for the test suite and linting).
- Make sure you fully understand the scope of the code you are
  reviewing; what it is and what it is not.
- Be mindful of clean code practices and `SOLID
  principles <https://en.wikipedia.org/wiki/SOLID>`__.
- Remember that you are reviewing the code, not the author!
- Positive feedbacks are more effective: *Let's use a list here instead
  of dict* is preferred over *Don't use a dict, use a list!*.
- Use clear vocabulary to let the author know if you are suggesting a
  change or you are demanding it.
- The main branch is expected to be stable and perfect. Therefore, any
  merge to the main (which is the code that you are reviewing) has to be
  working and producing the right/expected output. It is clean,
  documented, and tested.
- Make sure the changelog entry is formatted correctly and accurately
  summarizes changes made by the PR. The only change to the changelog
  should be the addition of the entry for the PR that is being reviewed.

After the review
----------------

Once the code gets the required two reviews (ideally one SME and one
SWE), and all signals are "go", the author merges it to the main. If
there are merge conflicts, the author resolves them. If solving the
merge conflict leads to a sufficiently large change to the code, the
code needs to be reviewed again.

After merging the Pull Request, the author deletes the branch.

Adding to the Changelog
-----------------------

All PRs are expected to have accompanying changelog entry in
```changelog.md`` <https://github.com/RuminantFarmSystems/MASM/blob/dev/changelog.md>`__.
The changelog entry must be placed under the section titled "*Next
Version Updates*". Each entry must contain the following information:

1. PR: Just the number, omit ``PR`` and ``#``. The number must be
   contained in square brackets, and immediately followed after by a
   link to the PR inside parentheses.
2. Major or minor change: How big are the changes in the PR? Would you
   nominate it for a Major version upgrade? Choose either "Major change"
   or "minor change" in square brackets.
3. Impact area: What parts of the codebase, inputs, or outputs are
   affected by this PR? Some options are Animal Module, Manure Module,
   Output structure, whole code base, etc. Put the impact area inside a
   pair of square brackets, and if there are multiple impact areas then
   include each in its own set of square brackets.
4. Description: briefly and concisely explain the change. Keep it short,
   yet informative. A few sentences should be enough. Avoid using broad
   and general statements such as ``update xyz``, it should be
   ``update xyz to abc``.

If ``changelog.md`` is not updated, the GitHub Action that runs on PRs
will fail and add a comment to the PR with a warning that the changelog
has not been updated yet. Updating the changelog is a necessary but not
sufficient condition for making the GitHub Action pass.

The Zen of Python
-----------------

If you write ``import this`` in a Python file, it generates the
following, consider using it during code review:

1.  Beautiful is better than ugly.
2.  Explicit is better than implicit.
3.  Simple is better than complex.
4.  Complex is better than complicated.
5.  Flat is better than nested.
6.  Sparse is better than dense.
7.  Readability counts.
8.  Special cases aren't special enough to break the rules.
9.  Although practicality beats purity.
10. Errors should never pass silently.
11. Unless explicitly silenced.
12. In the face of ambiguity, refuse the temptation to guess.
13. There should be one-- and preferably only one --obvious way to do
    it.
14. Although that way may not be obvious at first unless you're Dutch.
15. Now is better than never.
16. Although never is often better than *right* now.
17. If the implementation is hard to explain, it's a bad idea.
18. If the implementation is easy to explain, it may be a good idea.
19. Namespaces are one honking great idea -- let's do more of those!
