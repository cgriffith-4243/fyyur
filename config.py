import os
import getpass
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgres://{}@{}/{}'.format(getpass.getuser(), '127.0.0.1:5432', 'fyyur')
SQLALCHEMY_TRACK_MODIFICATIONS = False