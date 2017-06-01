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
                        [repo, commit_id, email, date, msg])
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


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--db', type=str, default='gitstats.sqlite')
    p.add_argument('paths', nargs='*')
    args = p.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute(schema)
    conn.text_factory = str

    if args.paths:
        print 'loading into ', args.db
        for path in args.paths:
            load(conn, path)

    print conn
