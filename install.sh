#!/bin/bash

echo 'Check for dependencies...'
python -c 'import jinja2,MySQLdb,redis,eventlet,bcrypt,chaofeng,tornado,yaml'

