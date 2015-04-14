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
