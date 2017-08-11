from distutils.core import setup

from pycrc import progname, version, url

setup(name = 'pycrc',
        version = version,
        description = 'Free, easy to use Cyclic Redundancy Check source code generator for C/C++',
        author = 'Thomas Pircher',
        author_email = 'tehpeh-web@tty1.net',
        url = url,
        packages = ['pycrc'],
        )
