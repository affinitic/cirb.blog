Introduction
============

This addon is integration of different Plone addons to provide a Blog Solution.

Dependencies
============

* collective.wpadmin
* collective.contentrules.yearmonth
* collective.recaptcha
* plone.formwidget.recaptcha
* collective.configviews

How to use
==========

You just have to add a folder in your website and call the @@cirb_blog_setup
view to turn this folder into a blog.

Next you have to configure your collection query:

* criteria: content type: Blog Entry
* criteria: review state: published
* sort on: effective date (reverse)


Credits
=======

Companies
---------

|cirb|_ CIRB / CIBG

* `Contact CIRB <mailto:irisline@irisnet.be>`_

|makinacom|_

  * `Planet Makina Corpus <http://www.makina-corpus.org>`_
  * `Contact Makina Corpus <mailto:python@makina-corpus.org>`_

People
------

- JeanMichel FRANCOIS aka toutpt <toutpt@gmail.com>

.. |cirb| image:: http://www.cirb.irisnet.be/logo.jpg
.. _cirb: http://cirb.irisnet.be
.. _sitemap: http://support.google.com/webmasters/bin/answer.py?hl=en&answer=183668&topic=8476&ctx=topic
.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com
.. _documentation: http://plone.org/documentation/kb/installing-add-ons-quick-how-to
