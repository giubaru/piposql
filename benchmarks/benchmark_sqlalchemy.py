#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
stream = sys.stderr
def info(s, end='\n'):
    stream.write(s)
    if end: stream.write(end)
info("* It benchmarks SQLAlchemy.")

from getpass import getuser
from sqlalchemy.sql import select
from sqlalchemy import create_engine, MetaData, Table, Column, String

# It seems SQLAlchemy is hard to co-work with native Psycopg2, so we use the
# its engine.
user_name = getuser()
engine = create_engine('postgresql://{}@localhost/{}'.format(user_name, user_name))
conn = engine.connect() # autocommit
info('* The connection is opened.')

metadata = MetaData()
testee = Table('testee', metadata,
    Column('id', String(128), primary_key=True),
    Column('name', String(128)),
)

def setup():

    conn.execute('drop table if exists testee')

    conn.execute('''
        create table
            testee (
                id varchar(128) primary key,
                name varchar(128)
            )
    ''')

    conn.execute(testee.insert().values([
        {'id': 'mosky.liu', 'name': 'Mosky Liu'},
        {'id': 'yiyu.liu', 'name': 'Yi-Yu Liu'}
    ]))

    info('* The data is created.')

def execute_select():
    return conn.execute(
        testee.select().where(testee.c.id == 'mosky.liu')
    ).fetchall()

def teardown():
    conn.execute('drop table testee')
    info('* The data is cleaned.')

if __name__ == '__main__':

    from timeit import timeit

    # init
    setup()

    n = 1000
    info('* Executing the bencmark (n={}) ...'.format(n))
    info('')
    print timeit(execute_select, number=n)
    info('')
    info('* Done.')

    # clean up
    teardown()
    conn.close()
    info('* The connection is closed.')
