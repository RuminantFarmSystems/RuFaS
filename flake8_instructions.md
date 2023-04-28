## RuFaS Flake8 styleguide

The RuFaS project uses [flake8](https://flake8.pycqa.org/en/latest/index.html) as the coding styleguide enforcement tool. Flake8 is a Python linting tool that checks the codebase for coding errors, styling issues, and complexity violations. 

The RuFaS Flake8 linting enforces all the [standard pep8 style guidelines for Python](https://peps.python.org/pep-0008/) except for 2: line length and complexity.

The RuFaS max line length guideline is 120 characters.
The RuFaS max complexity is 10.

This guide will help show how to install flake8 locally and to show you how to invoke it and to correct the styleguide violations present **before** pushing code to GitHub.

Whenever code is pushed to the RuFaS GitHub repository, it should first be checked locally using flake8 to ensure no additional styleguide violations are occurring.

Additionally, any fixes to legacy styleguide violations you can do within the files you're working on are greatly appreciated. Often these are quick fixes but may need to be done manually.

## Installing Flake8 Locally

To get started, first make sure that your virtual environment is activated.
Then install flake8 locally by opening an interactive shell or terminal and run this command:

    python<version> -m pip install flake8

For reference, in interactive shell command examples, angle brackets <\> are used to show places where user input may vary. They are not expected to be written into the eventual command. So when you run this script, it should look like this but with your specific python version in place of the one used here:

    python3.9 -m pip install flake8

In case you need your Python version, you can run this command in the same interactive shell:

    python --version

## Invoking Flake8 on your code

**Before** pushing your code to GitHub, check it with flake8. To do this, run the `cleanup.sh` script which looks **only** at any files that you have changed (committed and uncommitted) and checks for flake8 violations according to RuFaS' flake8 guidelines. This script should be run from the main `/MASM` directory (same directory as where you would run the simulation from).

    sh cleanup.sh

The above script will default to checking your branch's code against the master branch. If you need to compare it to a branch other than master \(e.g. your base branch is a part of a refactor), just add the branch you would like to compare the code to after the above command:

    sh cleanup.sh <branch-name>

This will hopefully minimize duplicating work.

## Fixing the Flake8 violations

When you run the above script on the code, a readout of the errors will appear in the terminal. It will show the location of each file where there is an error, give a specific flake8 code for the type of error, and give a printout of the specific line in the file where the error occurred:

    RUFAS/routines/feed/feed.py:804:61: E201 whitespace after '('
                self.new_forages.pop(self.new_forages.index( silo))
                                                            ^

Each flake8 violation has a specific code that explains what the style violation is (e.g. E201 for having whitespace after a `'('`). [This guide](https://www.flake8rules.com/) lists all the violations and shows examples of how to fix them.

When you've fixed the flake8 violations from the files you're pushing to GitHub, run the `cleanup.sh` script once again to ensure they've all been caught.

The goal is to not add any new flake8 violations to the RuFaS GitHub repo and to remove as many legacy violations as possible. Some violations, like code complexity (C901), may require a bigger fix and can be delayed if there isn't time or capacity to fix them.