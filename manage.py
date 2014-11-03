# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from tabapp import app
from tabapp.migrate import MigrateCommand


manager = Manager(app)
manager.add_command('db', MigrateCommand)

manager.run()
