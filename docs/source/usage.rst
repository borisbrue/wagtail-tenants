Usage
=====

.. _installation:

Installation
------------

To use Lumache, first install it using pip:

.. code-block:: console

   (.venv) $ pip install wagtail_tenants

Creating recipes
----------------

To retrieve a list of random ingredients,
you can use the ``wagtail_tenants.get_random_ingredients()`` function:

.. autofunction:: wagtail_tenants.get_random_ingredients

The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

.. autoexception:: wagtail_tenants.InvalidKindError

For example:

>>> import wagtail_tenants
>>> wagtail_tenants.get_random_ingredients()
['shells', 'gorgonzola', 'parsley']

