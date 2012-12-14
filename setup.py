from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='cirb.blog',
      version=version,
      description="Blog project for CIRB",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        ],
      keywords='plone blog',
      author='JeanMichel FRANCOIS aka toutpt',
      author_email='toutpt@gmail.com',
      url='https://github.com/CIRB/cirb.blog',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cirb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Scrawl',
          'collective.wpadmin',
          'plone.app.discussion',
          'collective.configviews',
          'collective.recaptcha',
          'plone.formwidget.recaptcha',
          'collective.cleanupzodb',
          # -*- Extra requirements: -*-
      ],
      extras_require=dict(
          test=['plone.app.testing'],
      ),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
