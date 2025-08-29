#!/usr/bin/python3
import sys
import os

sys.path.insert(0, '/var/www/flask_app/')

from index import app as application

if __name__ == "__main__":
    application.run()
