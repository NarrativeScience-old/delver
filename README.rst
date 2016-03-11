======
Delver
======

The ``delve`` command allows for the visual exploration of JSON data from the
command line, with the ability to see the types of data within as well as your
current location.::

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

This tool is typically used to look through large json payloads where seeing
the entirety of the file in a text editor or on a web page is
unwieldy/inconvenient.

Specifying a Data Transform
---------------------------

The ``delve`` script allows for the ability to specify a 'transform' step to
be applied before the data is actually explored. This might be used in the case
where unwanted fields in the json should be ignored. For example, consider the
following dataset:

  .. code-block:: javascript

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

When viewing/exploring the data, it may not be necessary to see the large
``company_id`` field on each of the ``subsidiary_companies``. If we defined the
following transform function in a module called ``transform.py`` which is within
the current directories scope (i.e. is listed in the ``PYTHONPATH`` or is
within the current directory), then we can appropriately ignore that field when
exploring.

  .. code-block:: python

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

To run the ``delve`` command with the transform, just specify the ``transform-func``
parameter::

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

And now we don't have to see those annoying company ids when exploring our data!

Getting Started
---------------

Simply install via ``pip``::

  $  pip install delver

This exposes the ``delve`` command line script (which corresponds to the
:py:func:`delver.delve:main` function).

Note that any transform functions should be either installed in the current
python interpreter's site-packages or should be available in local scope.
