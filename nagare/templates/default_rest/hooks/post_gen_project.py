import os

root = os.path.realpath(os.getcwd())
pwd = os.path.realpath(os.environ.get('PWD'))
if pwd:
    relroot = os.path.relpath(root, pwd)
    if '..' not in relroot:
        root = relroot

print("""\

Note:
  1. Edit the file '%(root)s/setup.py' to set the informations about your new application.
  2. Register your application with:
     - pip install -e %(root)s
""" % {'root': root})
