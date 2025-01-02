from setuptools import setup
from setuptools.command.install import install
from sys import prefix

from myMusicPathData import myMusicPathData

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        mmpd = myMusicPathData(install=True)

setup(
  name = 'music',
  py_modules = ['musicBase', 'matchMyMusic', 'matchMusicName', 'primeDirectory', 'myMusicPathData'],
  version = '0.0.1',
  cmdclass={'install': PostInstallCommand},
  description = 'A Python Wrapper for Music Data',
  long_description = open('README.md').read(),
  author = 'Thomas Gadfort',
  author_email = 'tgadfort@gmail.com',
  license = "MIT",
  url = 'https://github.com/tgadf/music',
  keywords = ['DB', 'music'],
  classifiers = [
    'Development Status :: 3',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ],
  install_requires=['jupyter_contrib_nbextensions'],
  dependency_links=[]
)
 
