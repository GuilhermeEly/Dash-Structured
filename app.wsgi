#!/usr/bin/python3
import sys

python_home = '/home/gadmin/Projects/venv/dash-fpy-env'

activate_this = python_home + '/bin/activate_this.py'

exec(open(activate_this).read())

sys.path.insert(0,"home/gadmin/Projects/FPY/Dash-Structured")
sys.path.insert(0,"home/gadmin/Projects/venv/dash-fpy-env/lib/python3.6")
from index import server as application
