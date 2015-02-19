# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from tabapp import create_app
from flask.ext.migrate import MigrateCommand


manager = Manager(create_app())
manager.add_command('db', MigrateCommand)

manager.run()
