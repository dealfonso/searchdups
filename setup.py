from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

from searchdups.version import VERSION

setup(
  name = 'searchdups',             # How you named your package folder
  packages = ['searchdups'],   
  version = VERSION,          # Start with a small number and increase it with every change you make
  license='Apache 2.0',       # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Searches for duplicate files in folders (recursively, if needed)',
  long_description = README,
  long_description_content_type = 'text/markdown',
  author = 'Carlos A.',             # Type in your name
  author_email = 'caralla@upv.es',  # Type in your E-Mail
  url = 'https://github.com/dealfonso/searchdups',   # Provide either the link to your github or to your website
  keywords = ['command line', 'cli', 'files', 'sysadmin' ],   # Keywords that define your package best
  install_requires=[           
        'tqdm', 
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Topic :: Utilities',
    'License :: OSI Approved :: Apache Software License',   # Again, pick a license
    'Programming Language :: Python :: 3',      # Specify which pyhton versions that you want to support
  ],
  entry_points = {
    'console_scripts' : [ 
      'searchdups=searchdups:searchdups',
    ]
  }
)