#!/usr/bin/env python

"""
Commands that update or process the application data.
"""
import app_config

from fabric.api import local, task

@task
def local_bootstrap():
    local('dropdb --if-exists %s' % app_config.PROJECT_SLUG)
    local('createdb %s' % app_config.PROJECT_SLUG)

@task
def drop_tables():
    for table in app_config.db.tables:
        print 'Dropping %s' % table
        table_obj = app_config.db[table]
        table_obj.drop()
