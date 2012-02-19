import os
import setuptools

# Some filesystems don't support hard links. Use the power of
# monkeypatching to overcome the problem.
import os, shutil
os.link = shutil.copy


setuptools.setup(name='rons',
      version='0.0.1',
      description='RonS - simple pub/sub Redis client for Tornado',
      author='Marek Majkowski',
      author_email='rons@popcnt.org',
      url='http://github.com/majek/rons#readme',
      packages=['rons'],
      platforms=['any'],
      license='MIT',
      zip_safe = True,
      )
