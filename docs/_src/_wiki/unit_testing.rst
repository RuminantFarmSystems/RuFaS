Unit testing
============

What is unit testing?
---------------------
Unit testing is a type of software testing where individual units or components of software are tested. The purpose is to validate that each unit of the software code performs as expected. Unit testing is done during the development (coding phase) of an application by the developers. Unit tests isolate a section of code and verify its correctness. A unit may be an individual function, method, procedure, module, or object. Unit testing is a WhiteBox testing technique that is usually performed by the developer. See https://realpython.com/python-testing/

Why are we investing in it?
---------------------------
In the Software Development Life Cycle (SDLC), Software Testing Life Cycle (STLC), and V-Model, unit testing is the first level of testing done before integration testing. It is a common practice to NOT accept any new code into the Version Control System (VCS, e.g., GitHub) without a properly written test suite. Unit testing is important because it ensures that individual components of the system are working correctly at the most granular level. Also, when modifying the code, we can be confident that the new code is not breaking anything because all unit tests are passing. Although we are not (yet) advocating the V-Model in RuFaS, here is a visualization for reference:

.. image:: https://media.geeksforgeeks.org/wp-content/uploads/V-Model.png
   :alt: The V model

How are we going to implement it?
---------------------------------
We have started the process by making sure all programmers are comfortable with writing unit tests in Python. When this is done, we will continue by compiling a list of a minimal set of unit tests. Then, we will prioritize them by counting the dependencies of each unit; i.e., the more other units depend on a unit, the higher its priority. We will work on adding unit tests starting from the highest priority.

Preferably, programmers should work on modules that they are most familiar with; however, for logistical reasons, we might need programmers to work on modules that they have not worked with before.

Note that unit testing and Sphinx documentation go hand in hand together.