# -*- coding: utf-8 -*-

from flask_script import Manager
from flask_migrate import MigrateCommand
from tabapp import create_app


manager = Manager(create_app())
manager.add_command('db', MigrateCommand)

manager.run()
