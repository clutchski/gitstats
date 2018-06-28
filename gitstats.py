#!/usr/bin/env python


import argparse
import os
import sqlite3
from datetime import datetime
import prettytable

from shell import shell


schema = """
    CREATE TABLE if not exists commits (
            repo text,
            author text,
            dt datetime,
            commit_hash text,
            message text
    )
"""

def load(conn, repo_dir):
    cwd = os.getcwd()
    try:
        os.chdir(repo_dir)

        try:
            repo = _sh('git config --get remote.origin.url')[0]
            print 'loading ', repo
            conn.execute('delete from commits where repo = ?', [repo])

            # unsuitable for really large repos but fine for me.
            commits = _sh('git log --date=short --format="%h\t%aE\t%ad\t%s"')
            i = 0
            for line in commits:
                i += 1
                s = line.strip().split("\t")
                if len(s) < 3:
                    raise Exception(s)
                commit_id = s[0]
                email = s[1]
                date = s[2]
                if len(s) == 4:
                    msg = s[3]
                if len(s) == 3:
                    msg = ""
                else:
                    msg = "\t".join(s[3:])
                conn.execute('insert into commits VALUES (?, ?, ?, ?, ?)',
                        [repo, email, date, commit_id, msg])
            print 'loaded %s commits' % i
        finally:
            conn.commit()
    finally:
        os.chdir(cwd)

def _sh(cmd):
    # this library is kinda crappy but who cares
    r = shell(cmd)
    if r.code != 0:
        raise Exception('error: %s' % "\n".join(r.errors()))
    return r.output()


def _connect(args):
    conn = sqlite3.connect(args.db)
    conn.execute(schema)
    conn.text_factory = str
    return conn

def _rename_author(args):
    conn = _connect(args)
    t = args.target[0]
    for f in args.source:
        q = '''
            update commits
              set author = ?
             where author = ?
             '''
        conn.execute(q, [t, f])
    conn.commit()

def _load(args):
    conn = _connect(args)
    for path in args.paths:
        load(conn, path)

def _authors(args):
    conn = _connect(args)
    q = '''select distinct author
               from commits
            where dt > ?
              and dt < ?
        order by author
            '''
    for i in conn.execute(q, [args.start, args.end]):
        print i[0]

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def _print(conn, author, start, end):
    q = '''
        select *
          from commits
         where author = ?
           and dt > ?
            and dt < ?
         order by dt asc, repo
            '''
    print author, start, end
    t = prettytable.PrettyTable(['repo', 'hash', 'dt', 'author', 'msg'])
    for r in conn.execute(q, [author, start, end]):
        t.add_row(r)
    print t


def _author(args):
    conn = _connect(args)
    for auth in args.authors:
        _print(conn, auth, args.start, args.end)

def _quarters(args):
    conn = _connect(args)
    bounds = [
        (args.year, 1, 1),
        (args.year, 3, 1),
        (args.year, 6, 1),
        (args.year, 9, 1),
        (args.year+1, 1, 1),
    ]
    dates = [datetime(*b) for b in bounds]
    quarters = [(dates[i], dates[i+1]) for i in range(len(bounds)-1)]
    for auth in args.authors:
        for i, (s, e) in enumerate(quarters):
            _print(conn, auth, s, e)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', type=str, default='gitstats.sqlite')
    subs = p.add_subparsers()

    auth = subs.add_parser("rename_author")
    auth.add_argument('target', nargs=1)
    auth.add_argument('source', nargs='+')
    auth.set_defaults(func=_rename_author)

    authors = subs.add_parser("authors")
    authors.add_argument('--start', type=valid_date, required=True)
    authors.add_argument('--end', type=valid_date, required=True)
    authors.set_defaults(func=_authors)

    quarters = subs.add_parser("quarters")
    quarters.add_argument('--year', type=int, default=2017, required=False)
    quarters.add_argument('authors', nargs='+')
    quarters.set_defaults(func=_quarters)

    summ = subs.add_parser("author")
    summ.add_argument('--start', type=valid_date, required=True)
    summ.add_argument('--end', type=valid_date, required=True)
    summ.add_argument('authors', nargs='+')
    summ.set_defaults(func=_author)

    lp = subs.add_parser("load")
    lp.add_argument('paths', nargs='+')
    lp.set_defaults(func=_load)

    args = p.parse_args()
    args.func(args)
