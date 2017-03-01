Time Tracker Models
===================

    >>> from timetracker.models import Category, Task

Let's make a category for our home tasks:

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

    >>> home.__name__
    'home'

    >>> home.__parent__ is None
    True

Let's add some categories under Home:

    >>> kitchen = home.add_category("Kitchen")
    >>> bed = home.add_category("Bedroom")
    >>> bath = home.add_category("Bathrooms",
    ...     id="bath",
    ...     description="Includes bathroom and washroom.")

These are given IDs automatically from the title (if one is not directly given)
and know their parent:

    >>> bed.id
    'bedroom'

    >>> bed.__parent__ is home
    True

If we try to add an ID we've used before, it will raise an error:

    >>> bed2 = home.add_category("Bedroom", id="bedroom")
    Traceback (most recent call last):
        ...
    KeyError: "Key 'bedroom' already in category"

Best to just omit the manually-given ID and let it find one:

    >>> bed2 = home.add_category("Bedroom")
    >>> bed2.id
    'bedroom-2'

Tasks
-----

Tasks can be created directly:

    >>> task1 = Task("one", "Task One")

Tasks can have a number of minutes associated with the task:

    >>> task1 = Task("one", "Task One", mins=90)

    >>> task2 = Task("two", "Task Two", mins="not valid")
    Traceback (most recent call last):
        ...
    ValueError: Task mins must be None or an integer

Typically, though, you'll add a task to a category with a convenience method:

    >>> buy = home.add_task("Buy home")
    >>> clean = kitchen.add_task("Clean Kitchen", id="clean")
    >>> scrub = bath.add_task("Scrub", description="Both toilet and bath.")

The minutes can be passed in when using the convenience API:

    >>> dishes = kitchen.add_task("Wash dishes", mins=20)

Listing Items
-------------

We can get a list of our categories:

    >>> list(home.categories())
    [<Category bath "Bathrooms">,
     <Category bedroom "Bedroom">,
     <Category bedroom-2 "Bedroom">,
     <Category kitchen "Kitchen">]

And a list of tasks:

    >>> list(home.tasks())
    [<Task scrub "Scrub">,
     <Task buy-home "Buy home">,
     <Task clean "Clean Kitchen">,
     <Task wash-dishes "Wash dishes">]

We can also get a total number of minute of tasks:

    >>> home.total_mins()
    20

    >>> home['bedroom'].total_mins()
    0

Deleting Items
--------------

Tasks can easily be deleted:

    >>> "buy-home" in home
    True

    >>> buy.delete()

    >>> "buy-home" in home
    False

Categories can be deleted:

    >>> "bedroom-2" in home
    True

    >>> bed2.delete()

    >>> "bedroom-2" in home
    False

Categories that contain subcategories or tasks cannot normally be deleted:

    >>> kitchen.delete()
    Traceback (most recent call last):
        ...
    Exception: Cannot delete Category kitchen without deleting children

You can provide a True value for the recurse option to delete these:

    >>> kitchen.delete(recurse=True)

    >>> "kitchen" in home
    False
