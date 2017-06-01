#!/usr/bin/env python

import argparse
import subprocess


schema = """
    CREATE TABLE commits (
            repo text,
            author text,
            dt datetime,
            commit_hash text,
            message text
    )
"""


def load(db):
    pass

if __name__ != '__main__':
    main()
