# Delver

The `delve` command allows for the visual exploration of JSON data from the
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

# Advanced Features

This tool is typically used to look through large json payloads where seeing
the entirety of the file in a text editor or on a web page is
unwieldy/inconvenient. The advanced features allow for simplifying payloads or making
them easier to navigate and explore.

## Specifying a Data Transform

The ``delve`` script allows for the ability to specify a 'transform' step to
be applied before the data is actually explored. This might be used in the case
where unwanted fields in the json should be ignored. For example, consider the
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

# Getting Started

## Requirements

The `delve` tool requires that Python is installed as well as the `six` package (taken
care of via the installation method below), which allows for compatibility between Python 2
and Python 3.

Specifically, `delve` has been tested with Python versions 2.7.8 and 3.4.0.

## Installation

Simply install via `pip`:

```
$  pip install delver
```

This exposes the `delve` command line script (which corresponds to the
`delver.delve:main` function).

Note that any transform functions should be either installed in the current
python interpreter's site-packages or should be available in local scope.


# Development

Setting up the development environment does not vary between python versions. See the
instructions below for more details on how to get up and running. We welcome pull
requests on new features or fixes!

Note that these instructions assume the repo has been cloned locally and that
the user is in the top-level directory:

```
$ git clone https://github.com/NarrativeScience/delver.git
$ cd delver
```

## Running Tests

When doing development, the tests can be executed by using
[pytest](http://docs.pytest.org/en/latest/getting-started.html).

First install the package requirements as well as the test-specific requirements:

```
$ pip install -r requirements.txt
$ pip install -r test_requirements.txt
```

Executing the tests just involves running the `pytest` command:

```
$ pytest
============================= test session starts ==============================
platform darwin -- Python 3.4.0, pytest-3.0.3, py-1.4.31, pluggy-0.4.0
rootdir: /Users/asippel/delver, inifile:
collected 4 items

tests/test_delver.py ....

=========================== 4 passed in 0.05 seconds ===========================
```
