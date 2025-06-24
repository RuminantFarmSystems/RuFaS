Code Coverage
=============

What is code coverage?
----------------------
Code coverage is the percentage of code that is covered by automated tests. Code coverage measurement simply determines which statements in a body of code have been executed through a test run, and which statements have not. In general, a code coverage system collects information about the running program and then combines that with source information to generate a report on the test suite’s code coverage.

See `About Code Coverage <https://confluence.atlassian.com/clover/about-code-coverage-71599496.html>`_.

Why is it important?
--------------------
Code coverage is part of a feedback loop in the development process. As tests are developed, code coverage highlights aspects of the code that may not be adequately tested and which require additional testing. This loop will continue until coverage meets some specified target.

Code coverage also helps us be sure that we are doing TDD correctly and not leaving holes in the test suite.

How can we increase it?
-----------------------
- Over time, we will identify the more important parts of the code which are lacking coverage, and we will work on adding tests for them.
- When a programmer adds code to the code base, the expectation is that they have followed TDD; therefore, the coverage for the new code should be 100%.