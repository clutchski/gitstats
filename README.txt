
SETUP
=====

    pip install prettytable shell


LOAD
====
clone repos you want to analyze:

    git clone github.com/foo/bar
    git clone github.com/foo/baz

load their commits:

    $ ./gitstats.py load <path_to_repo>


QUERY
=====

find all authors:

    $ ./gitstats.py authors --start 2017-01-01 --end 2018-01-01

see commits by an author:

    $ ./gitstats.py author --start 2017-01-01 --end 2018-01-01 user@example.com

see a quarterly summary:

    $ ./gitstats.py quarters --year 2018 user@example.com

or run your own queries:

    $ sqlite3 gitstats.sqlite
    > .schema
