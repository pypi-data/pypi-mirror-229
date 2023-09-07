# dependencies management in in setuptools
# https://setuptools.pypa.io/en/latest/userguide/dependency_management.html

from setuptools import setup
from os import path
import abbts_blp

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='abbts_blp',
    version=abbts_blp.__VERSION__,
    author='Pascal Helfenstein',
    author_email='pascal.helfenstein@abbts.ch',
    # scripts=['bin/script1','bin/script2'],
    url='https://github.com/p-d-h/abbts_blp',
    license='LICENSE.txt',
    description='abbts_blp',
    long_description=long_description,
    long_description_content_type='text/markdown',  # Optional (see note above)
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    packages=['abbts_blp'],
    # package_data={'': ['*.ini']},
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        'pyserial >= 3.5',
        'Pillow >= 9.3',
    ],
)
