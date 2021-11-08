NTTable test
============

To install::

    git clone https://github.com/thomascobb/nt_table_test.git
    cd nt_table_test
    pipenv install

To run::

    pipenv run python nt_table_test.py

It will print out the database it made. You can then get the table::

    $ pvget NT-TABLE-IOC:TABLE
    NT-TABLE-IOC:TABLE
    enabled trigger repeats
        0       0      12
        0       1       1
        0       2       2
        0       0       3
        0       1       4
        0       2       5
        0       0       6
        0       1       7
        0       2       8
        0       0       9

It will update itself every second::

    $ pvget NT-TABLE-IOC:TABLE
    NT-TABLE-IOC:TABLE
    enabled trigger repeats
        0       0      23
        0       1       1
        0       2       2
        0       0       3
        0       1       4
        0       2       5
        0       0       6
        0       1       7
        0       2       8
        0       0       9

And you can put to it::

    $ pvput NT-TABLE-IOC:TABLE '{"value":{"c1":[0], "c2":[1], "c3":[2]}}'
    Old :
    enabled trigger repeats
        0       0      50
        0       1       1
        0       2       2
        0       0       3
        0       1       4
        0       2       5
        0       0       6
        0       1       7
        0       2       8
        0       0       9
    New :
    enabled trigger repeats
        0       1       2

But monitors are not currently working::

    $ pvget -m NT-TABLE-IOC:TABLE
    NT-TABLE-IOC:TABLE
    enabled trigger repeats
        0       0       1
        0       1       1
        0       2       2
        0       0       3
        0       1       4
        0       2       5
        0       0       6
        0       1       7
        0       2       8
        0       0       9



