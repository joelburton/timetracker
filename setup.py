import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'transaction',
    'ZODB',
]

tests_require = [
    'pytest',
    'pytest-cov',
]

setup(name='timetracker',
      version='0.0',
      description='Console-based time-tracking system.',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
      ],
      author='Joel Burton',
      author_email='joel@joelburton.com',
      url='https://github.com/joelburton/timetracker/',
      keywords='time tracker',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      tracker = timetracker.scripts.tracker:main
      """,
      )
