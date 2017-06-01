#!/usr/bin/env python


import argparse
import os
import sqlite3

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
    q = 'select distinct author from commits order by author'
    for i in conn.execute(q):
        print i[0]


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', type=str, default='gitstats.sqlite')
    subs = p.add_subparsers()

    auth = subs.add_parser("rename_author")
    auth.add_argument('target', nargs=1)
    auth.add_argument('source', nargs='+')
    auth.set_defaults(func=_rename_author)

    authors = subs.add_parser("authors")
    authors.set_defaults(func=_authors)

    lp = subs.add_parser("load")
    lp.add_argument('paths', nargs='+')
    lp.set_defaults(func=_load)

    args = p.parse_args()
    args.func(args)
