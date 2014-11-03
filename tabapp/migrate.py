# -*- coding: utf-8 -*-

from flask.ext.migrate import Migrate, MigrateCommand
from tabapp import app
from tabapp.models import db


migrate = Migrate(app, db)
