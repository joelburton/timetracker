===================
Time Tracker Models
===================

The time tracker application uses "persistent Python objects". These are
relatively normal Python classes that we can create and update using the
standard Python dictionary syntax. However, since they descend from
the `persistent` library, they can transparently be saved in the ZODB
object database.

Models
======

For now, let's look at the object types themselves:

.. code-block:: python

    >>> from timetracker.models import Category, Task

Let's make a category for our home tasks:

.. code-block:: python

    >>> home = Category("home", "Home")
    >>> home.id
    'home'
    >>> home.title
    'Home'
    >>> home.description
    ''
    >>> home
    <Category home "Home">

When this gets stored in the object database, it will need a name and reference
to the parent. We use the ID for the name, and the parent reference is initially
blank:

.. code-block:: python

    >>> home.__name__
    'home'

    >>> home.__parent__ is None
    True

Let's add some categories under Home:

.. code-block:: python

    >>> kitchen = home.add_category("Kitchen")
    >>> bed = home.add_category("Bedroom")
    >>> bath = home.add_category("Bathrooms",
    ...     id="bath",
    ...     description="Includes bathroom and washroom.")

These are given IDs automatically from the title (if one is not directly given)
and know their parent:

.. code-block:: python

    >>> bed.id
    'bedroom'

    >>> bed.__parent__ is home
    True

If we try to add an ID we've used before, it will raise an error:

.. code-block:: python

    >>> bed2 = home.add_category("Bedroom", id="bedroom")
    Traceback (most recent call last):
        ...
    KeyError: "Key 'bedroom' already in category"

Best to just omit the manually-given ID and let it find one:

.. code-block:: python

    >>> bed2 = home.add_category("Bedroom")
    >>> bed2.id
    'bedroom-2'

Tasks
-----

Tasks can be created directly:

.. code-block:: python

    >>> task1 = Task("one", "Task One")

Tasks can have a number of minutes associated with the task:

.. code-block:: python

    >>> task1 = Task("one", "Task One", mins=90)

    >>> task2 = Task("two", "Task Two", mins="not valid")
    Traceback (most recent call last):
        ...
    ValueError: Task mins must be None or an integer

Typically, though, you'll add a task to a category with a convenience method:

.. code-block:: python

    >>> buy = home.add_task("Buy home")
    >>> clean = kitchen.add_task("Clean Kitchen", id="clean")
    >>> scrub = bath.add_task("Scrub", description="Both toilet and bath.")

The minutes can be passed in when using the convenience API:

.. code-block:: python

    >>> dishes = kitchen.add_task("Wash dishes", mins=20)

Listing Items
-------------

We can get a list of our categories:

.. code-block:: python

    >>> list(home.categories())
    [<Category bath "Bathrooms">,
     <Category bedroom "Bedroom">,
     <Category bedroom-2 "Bedroom">,
     <Category kitchen "Kitchen">]

And a list of tasks:

.. code-block:: python

    >>> list(home.tasks())
    [<Task scrub "Scrub">,
     <Task buy-home "Buy home">,
     <Task clean "Clean Kitchen">,
     <Task wash-dishes "Wash dishes">]

We can also get a total number of minute of tasks:

.. code-block:: python

    >>> home.total_mins()
    20

    >>> home['bedroom'].total_mins()
    0

This normally sums up all tasks *anywhere* below that category;
to get the sum of tasks only directly inside that category, pass a
false value for `recurse`:

.. code-block:: python

    >>> home.total_mins(recurse=False)
    0

    >>> home['kitchen'].total_mins(recurse=False)
    20

Deleting Items
--------------

Tasks can easily be deleted:

.. code-block:: python

    >>> "buy-home" in home
    True

    >>> buy.delete()

    >>> "buy-home" in home
    False

Categories can be deleted:

.. code-block:: python

    >>> "bedroom-2" in home
    True

    >>> bed2.delete()

    >>> "bedroom-2" in home
    False

Categories that contain subcategories or tasks cannot normally be deleted:

.. code-block:: python

    >>> kitchen.delete()
    Traceback (most recent call last):
        ...
    Exception: Cannot delete Category kitchen without deleting children

You can provide a True value for the recurse option to delete these:

.. code-block:: python

    >>> kitchen.delete(recurse=True)

    >>> "kitchen" in home
    False

Saving in a Database
====================

Let's ensure we can store these objects in the ZODB. :

.. code-block:: python

    >>> import ZODB

We'll make a connection to an in-memory database:

.. code-block:: python

    >>> db = ZODB.DB(None)
    >>> conn = db.open()

The "root" of our database is the top object. This is neither a
category nor a task, but just a dictionary-like thing to hold the
top-level categories:

.. code-block:: python

    >>> root = conn.root()

Let's add a category to it:

.. code-block:: python

    >>> root['joel'] = joel = Category('joel', "Joel's Tasks")
    >>> joel.add_task("Play with ZODB")
    <Task play-with-zodb "Play with ZODB">

Transactions
------------

The ZODB uses transactions, so while we can see this, it isn't
saved yet for other people. We can test this by opening a second,
independent connection to the same database:

.. code-block:: python

    >>> conn2 = db.open()
    >>> root2 = conn2.root()

    >>> 'joel' in root2
    False

    >>> conn2.close()

If we commit the transaction, then it will be visible to others:

.. code-block:: python

    >>> import transaction
    >>> transaction.commit()

We can prove this by opening a fresh connection to the db and
seeing that the new category is there:

.. code-block:: python

    >>> conn2 = db.open()
    >>> root2 = conn2.root()

    >>> 'joel' in root2
    True

    >>> conn2.close()

Aborting
--------

Of course, we can also abort a transaction:

.. code-block:: python

    >>> joel.add_task("Foo")
    <Task foo "Foo">

    >>> "foo" in joel
    True

    >>> transaction.abort()
    >>> "foo" in joel
    False
