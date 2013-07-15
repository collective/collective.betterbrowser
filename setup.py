from setuptools import setup, find_packages

version = '0.1'

docs = ('README.rst', 'CONTRIBUTORS.rst', 'CHANGES.rst')
long_description = '\n'.join(open(f).read() for f in docs)

setup(name='collective.betterbrowser',
      version=version,
      description=(
          'Inspect the contents of your plone.testing browser instance in a '
          'real browser (like Firefox), and more.'
      ),
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Intended Audience :: Developers",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='mechanize browser testing plone',
      author='Denis Krienbuehl',
      author_email='denis.krienbuehl@gmail.com',
      url='https://github.com/collective/collective.betterbrowser',
      license='MIT',
      packages=find_packages(),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.testing'
      ],
      extras_require={
          'pyquery': ['pyquery']
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
