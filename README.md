===============
autopep8_quotes
===============

.. image:: https://travis-ci.org/zoynels/autopep8_quotes.svg?branch=master
    :target: https://travis-ci.org/zoynels/autopep8_quotes
    :alt: Build status

Modifies strings to all use the same quote where possible.


Example
=======

After running::

    $ autopep8_quotes --in-place example.py

this code

.. code-block:: python

    x = "abc"
    y = 'hello'

gets formatted into this

.. code-block:: python

    x = 'abc'
    y = 'hello'
