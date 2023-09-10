libexcs
=======

*"An exceptional library"*


Installing
~~~~~~~~~~

Just use pip:

::

   pip install libexcs


Usage
-----

::

   import datetime
   from libexcs import root

   print("# 1. Subclass, override '_template_' class attribute and define class annotations")

   class DerivedException(root.RootException):
       _template_ = "Having count={count} for owner={owner}"

       count: int
       owner: str
       extra: datetime.datetime

   print("# ----")

   ts = datetime.datetime.utcnow()
   try:
       print("# 2. Raise with kwargs matching the template field names")
       raise DerivedException(count=42,
                              owner="somebody",
                              extra=dict(timestamp=ts))
   except Exception as e:
       print("# ----")
       print("# 3. Play with raised exceptions")
       print(f"# Raised exception 'e': {e}")

       print(f">> e.count == {e.count}")
       print(f">> e.owner == {e.owner}")
       print(f">> e.extra == {e.extra}")

       r = repr(e)
       print(f">> Exception repr: {r}")
       print("# Reconstructing exception from repr...")
       e2 = eval(r)
       print("# Comparing attribute from original and reconstructed exceptions...")
       print(f">> {e2.count} == {e.count} : {e2.count == e.count}")

   print("# ----")
   print("# 4. See behaviour on incorrect usage")

   print("# You will receive TypeError on missing")
   try:
       raise DerivedException(count=42)
   except Exception as e:
       print(f">> {e!r}")


Running the tests
-----------------

Simply run tox:

::

   tox


Contributing
------------

Contact me through `Issues <https://gitlab.com/pyctrl/libexcs/-/issues>`__.

Versioning
----------

We use `SemVer <http://semver.org/>`__ for versioning. For the versions
available, see the `tags on this
repository <https://gitlab.com/pyctrl/libexcs/-/tags>`__.

Authors
-------

-  **Dima Burmistrov** - *Initial work* -
   `pyctrl <https://gitlab.com/pyctrl/>`__

*Special thanks to* `Eugene Frolov <https://github.com/phantomii/>`__ *for inspiration.*

License
-------

This project is licensed under the MIT/X11 License - see the
`LICENSE <https://gitlab.com/pyctrl/libexcs/-/blob/main/LICENSE>`__ file for details
