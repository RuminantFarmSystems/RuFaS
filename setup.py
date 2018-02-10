#!/usr/bin/env python3

#from distutils.core import setup

#setup(name='RUFAS',
#      version='1.0',
#      description='Ruminant Farm Systems Model',
#      author='Kass Chupongstimun',
#      author_email='kass_c@hotmail.com',
#      url='xxx',
#      packages=['RUFAS'],
#     )

import cx_Freeze

cx_Freeze.setup(name = "RUFAS",
                version = "1.1",
                description = "Ruminant Farm Systems Model",
                author='Kass Chupongstimun & Jit Patil',
                author_email='kass_c@hotmail.com',
                executables = [cx_Freeze.Executable("main.py",
                                                    targetName = 'RUFAS')]
                )
                               
