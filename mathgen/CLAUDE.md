# Mathgen

Contains classes and functions for generating practice problems and problem sets. 

## Structure

* `mathgen/common/problems.py` contains `Problem` datatype and `ProblemSetBaseClass` classes that problem sets inherit from. It also includes functions for generating problem sets and a `InteractiveSession` class for interactive terminal sessions.
* `mathgen/lessons` contains Python files grouped into lessons that contain problems that inherit from the ProblemSetBaseClass.
* `mathgen/common/utils.py` contains some common math operations. 

## Conventions

* All problems inherit from the `ProblemSetBaseClass` and are grouped into Python files in the `mathgen/lessons` directory.


