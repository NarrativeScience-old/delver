# Delver

[![CircleCI](https://circleci.com/gh/NarrativeScience/delver/tree/master.svg?style=shield)](https://circleci.com/gh/NarrativeScience/delver/tree/master) [![](https://img.shields.io/pypi/v/pydelver.svg)](https://pypi.org/pypi/pydelver/) [![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

The Delver tool allows for the visual exploration of nested objects, which can
be useful for coming to grips with unfamiliar data or learning the structure of
a new codebase. In particular, this package exposes a command line tool `delve`
as well as a Python library which can be used to understand JSON structures
and arbitrary Python objects.

Features:

- Command line tool for exploring JSON data
- Support for interactive exploration of Python objects within debugger

Table of Contents:

- [Installation](#getting-started)
- [Guide](#guide)
- [Development](#development)

# Getting Started

## Requirements

The `delve` tool requires that Python is installed as well as the `six` package (taken
care of via the installation method below), which allows for compatibility between Python 2
and Python 3.

Specifically, `delve` has been tested with Python versions 2.7.8 and 3.7.2.

## Installation

Simply install via `pip`:

```
$  pip install pydelver
```

This exposes the `delve` command line script (which corresponds to the
`delver.delve:main` function).

Note that any transform functions should be either installed in the current
python interpreter's site-packages or should be available in local scope.


# Guide

## Command Line Tool

The `delve` command allows for the exploration of JSON data from the
command line, with the ability to see the types of data within as well as your
current location:

```
$  delve test_delver.json
-------------------------------------------------------------------------------
Dict (length 3)
+-----+--------+------------------------+
| Idx | Key    | Data                   |
+-----+--------+------------------------+
| 0   | league | MidwestDataAwesomeness |
| 1   | sport  | Data Innovation        |
| 2   | teams  | <list, length 2>       |
+-----+--------+------------------------+
[<key index>, u, q] -->
```

This displays the top level keys as well as a description of their values for the
*test_delver.json* file. A number of input options are printed at the bottom which
indicate that a user can either:

* Select a *key index* from the available `Idx` values in the column on the left
* Select *u*
* Select *q*

Selecting a *key index* will navigate into that value and display information
about any keys and/or values at that level. For example, selecting 2 would navigate
into the *teams* object, which we can now see is a list of dictionaries:

```
-------------------------------------------------------------------------------
At path teams
List (length 2)
+-----+------------------+
| Idx | Data             |
+-----+------------------+
| 0   | <dict, length 4> |
| 1   | <dict, length 4> |
+-----+------------------+
[<int>, u, q] --> 0
```

From this point, the user can select *u* to go back **up** one level to the top, or they can
further delve by selecting an index. For example if the user selects 0:

```
-------------------------------------------------------------------------------
At path teams->0
Dict (length 4)
+-----+-------------+------------------+
| Idx | Key         | Data             |
+-----+-------------+------------------+
| 0   | mascot      | TRex             |
| 1   | players     | <list, length 6> |
| 2   | team symbol | ☃                |
| 3   | teamname    | editors          |
+-----+-------------+------------------+
[<key index>, u, q] -->
```

At this point, the user can continue navigating using the indices, return to a higher
level using *u*, or enter *q* to exit.

## Python Library

The `Delver` class, which powers the `delve` tool above, can be used
directly when working in a python interpreter:

```ipython
In [1]: import delver

In [2]: test_object = {'foo': 200, 'bar': False, 'baz': [1, 2, 3]}

In [3]: delver.run(test_object)
-------------------------------------------------------------------------------
At path: root
Dict (length 3)
+-----+-----+------------------+
| Idx | Key | Data             |
+-----+-----+------------------+
| 0   | bar | False            |
| 1   | baz | <list, length 3> |
| 2   | foo | 200              |
+-----+-----+------------------+
[<key index>, u, q] -->
```

This can be useful when debugging software (it works the same in
[`pdb`](https://docs.python.org/2/library/pdb.html) or
[`ipdb`](https://github.com/gotcha/ipdb)), as well as when working in a new or
unfamiliar codebase. For example, it's very easy to see what public methods
and classes are defined in a package:

```ipython
In [1]: import delver

In [2]: import unittest

In [3]: delver.run(unittest)
-------------------------------------------------------------------------------
At path: root
+-----+-------------------+---------------------------------------------------+
| Idx | Attribute         | Data                                              |
+-----+-------------------+---------------------------------------------------+
| 0   | BaseTestSuite     | <class 'unittest.suite.BaseTestSuite'>            |
| 1   | FunctionTestCase  | <class 'unittest.case.FunctionTestCase'>          |
| 2   | SkipTest          | <class 'unittest.case.SkipTest'>                  |
| 3   | TestCase          | <class 'unittest.case.TestCase'>                  |
| 4   | TestLoader        | <class 'unittest.loader.TestLoader'>              |
| 5   | TestProgram       | <class 'unittest.main.TestProgram'>               |
| 6   | TestResult        | <class 'unittest.result.TestResult'>              |
| 7   | TestSuite         | <class 'unittest.suite.TestSuite'>                |
| 8   | TextTestResult    | <class 'unittest.runner.TextTestResult'>          |
| 9   | TextTestRunner    | <class 'unittest.runner.TextTestRunner'>          |
| 10  | case              | <module 'unittest.case' from                      |
|     |                   | '/Users/nscience/python2.7/unittest/case.pyc'>    |
| 11  | defaultTestLoader | <unittest.loader.TestLoader object at 0x10eeb0d10>|
| 12  | expectedFailure   | <function expectedFailure at 0x10eeab8c0>         |
| 13  | findTestCases     | <function findTestCases at 0x10eeb59b0>           |
| 14  | getTestCaseNames  | <function getTestCaseNames at 0x10eeb58c0>        |
| 15  | installHandler    | <function installHandler at 0x10eeb5f50>          |
| 16  | loader            | <module 'unittest.loader' from                    |
|     |                   | '/Users/nscience/python2.7/unittest/loader.pyc'>  |
| 17  | main              | <class 'unittest.main.TestProgram'>               |
| 18  | makeSuite         | <function makeSuite at 0x10eeb5938>               |
| 19  | registerResult    | <function registerResult at 0x10eeb5e60>          |
| 20  | removeHandler     | <function removeHandler at 0x10eec2050>           |
| 21  | removeResult      | <function removeResult at 0x10eeb5ed8>            |
| 22  | result            | <module 'unittest.result' from                    |
|     |                   | '/Users/nscience/python2.7/unittest/result.pyc'>  |
| 23  | runner            | <module 'unittest.runner' from                    |
|     |                   | '/Users/nscience/python2.7/unittest/runner.pyc'>  |
| 24  | signals           | <module 'unittest.signals' from                   |
|     |                   | '/Users/nscience/python2.7/unittest/signals.pyc'> |
| 25  | skip              | <function skip at 0x10eeab758>                    |
| 26  | skipIf            | <function skipIf at 0x10eeab7d0>                  |
| 27  | skipUnless        | <function skipUnless at 0x10eeab848>              |
| 28  | suite             | <module 'unittest.suite' from                     |
|     |                   | '/Users/nscience/python2.7/unittest/suite.pyc'>   |
| 29  | util              | <module 'unittest.util' from                      |
|     |                   | '/Users/nscience/python2.7/unittest/util.pyc'>    |
+-----+-------------------+---------------------------------------------------+
[<attr index>, u, q] -->
```

Moving through the hierarchy, then, enables quickly understanding all the parts
that make up the unfamiliar library.

## Advanced Features

This tool is typically used to look through large JSON payloads where seeing
the entirety of the file in a text editor or on a web page is
unwieldy/inconvenient. The advanced features allow for simplifying payloads or making
them easier to navigate and explore.

### Specifying a Data Transform from the Command Line

The ``delve`` script allows for the ability to specify a 'transform' step to
be applied before the data is actually explored. This might be used in the case
where unwanted fields in the JSON should be ignored. For example, consider the
following dataset:

```javascript
{
   "company_name": "MegaCorp",
   "company_location": "Gotham",
   "company_description": "Innovator in the corporate activity space",
   "subsidiary_companies": [
     {
       "company_name": "tinycorp",
       "company_location": "Gotham",
       "company_id": "2391235091875091348523472634782352354981723409128734019283471203941239085"
    },
    {
      "company_name": "smallcompany",
      "company_location": "Podunk",
      "company_id": "3912750918273410928347120938751098234712034981250917123049817234091283471"
    }
  ]
}
```

When viewing/exploring the data, it may not be necessary to see the large
`company_id` field on each of the `subsidiary_companies`. If we defined the
following transform function in a module called `transform.py` which is within
the current directories scope (i.e. is listed in the `PYTHONPATH` or is
within the current directory), then we can appropriately ignore that field when
exploring.

```python
def remove_company_ids(payload):
    """Given a company payload, remove all of the 'company_id' fields
    within the company dictionaries listed under 'subsidiary_companies'.

    :param payload: dictionary containing company information with company
        id fields to remove
    :type payload: ``dict``

    :return: a modified *payload* without any 'company_id' fields
    :rtype: ``dict``
    """
    for company in payload.get('subsidiary_companies', []):
        del company['company_id']
    return payload
```

To run the `delve` command with the transform, just specify the `transform-func`
parameter:

```
$  delve company_info.json --transform-func transform:remove_company_ids
-------------------------------------------------------------------------------
Dict (length 4)
+-----+----------------------+-------------------------------------------+
| Idx | Key                  | Data                                      |
+-----+----------------------+-------------------------------------------+
| 0   | company_description  | Innovator in the corporate activity space |
| 1   | company_location     | Gotham                                    |
| 2   | company_name         | MegaCorp                                  |
| 3   | subsidiary_companies | <list, length 2>                          |
+-----+----------------------+-------------------------------------------+
[<key index>, u, q] --> 3
-------------------------------------------------------------------------------
At path subsidiary_companies
List (length 2)
+-----+------------------+
| Idx | Data             |
+-----+------------------+
| 0   | <dict, length 2> |
| 1   | <dict, length 2> |
+-----+------------------+
[<int>, u, q] --> 0
-------------------------------------------------------------------------------
At path subsidiary_companies->0
Dict (length 2)
+-----+------------------+----------+
| Idx | Key              | Data     |
+-----+------------------+----------+
| 0   | company_location | Gotham   |
| 1   | company_name     | tinycorp |
+-----+------------------+----------+
[<key index>, u, q] -->
```

And now we don't have to see those annoying company ids when exploring our data!

# Development

Setting up the development environment does not vary between python versions. See the
instructions below for more details on how to get up and running. We welcome pull
requests on new features or fixes (especially if they involve new
[handlers](src/delver/handlers.py))!

Note that these instructions assume the repo has been cloned locally and that
the user is in the top-level directory:

```
$ git clone https://github.com/NarrativeScience/delver.git
$ cd delver
```

## Running Tests

When doing development, the tests can be executed by using
[tox](https://tox.readthedocs.io/en/latest/).

First install the package requirements as well as the test-specific requirements:

```bash
pip install pre-commit tox
pre-commit install
```

Then executing the tests just involves running:

```bash
tox
```
