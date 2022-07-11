Installation
============

From GitHub
###########
 - Clone the repository with ``git clone https://github.com/nwithan8/pycketcasts.git``
 - Enter project folder with ``cd pycketcasts``
 - Install requirements with ``pip install -r requirements.txt``


From PyPi
#########
 - Run ``pip install pycketcasts``

Setup
============
Import the ``PocketCast`` class from the pocketcasts module

.. code-block:: python

    from pycketcasts import PocketCast
    api = PocketCast(email="MY_EMAIL", password="MY_PASSWORD")
