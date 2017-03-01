"""Models for time tracking.

Categories contain tasks and can also contain categories in a nested manner.
"""

from persistent import Persistent
from persistent.mapping import PersistentMapping

from .slugify import slugify_unique


class Category(PersistentMapping):
    """Category for time-tracking tasks.

    Categories can contain other categories to any depth. Categories can also
    contain tasks.
    """

    def __init__(self, id, title, description="", parent=None):
        """Create category."""

        super().__init__()

        self.__parent__ = parent

        self.id = id
        self.title = title
        self.description = description

    def __repr__(self):
        return '<Category {} "{}">'.format(self.id, self.title)

    @property
    def __name__(self):
        """Required for traversal; use the id as the name."""

        return self.id

    def add_task(self, title, description="", id=None, mins=None):
        """Add task to category.

        If an ID isn't given, it will be calculated from the title (in a way
        that guarantees uniqueness).
        """

        if id is not None:
            if id in self:
                raise KeyError("Key '{}' already in category".format(id))
        else:
            id = slugify_unique(title, self.keys())

        task = Task(id, title, description, mins=mins, parent=self)
        self[id] = task
        return task

    def add_category(self, title, description="", id=None):
        """Add category to category.

        If an ID isn't given, it will be calculated from the title (in a way
        that guarantees uniqueness).
        """

        if id is not None:
            if id in self:
                raise KeyError("Key '{}' already in category".format(id))
        else:
            id = slugify_unique(title, self.keys())

        cat = Category(id, title, description, parent=self)
        self[id] = cat
        return cat

    def categories(self, recurse=True):
        """Get categories in this category.

        With `recurse`, this will find all descendants. Without, it will only include
        direct children.

        The order is by ID at each level::

            b
            a
              a     becomes [a, a (inner), c, b]
              c
        """

        for k, v in sorted(list(self.items())):
            if isinstance(v, Category):
                yield v

                if recurse:
                    yield from v.categories(True)

    def tasks(self, recurse=True):
        """Get tasks in this category.

        With `recurse`, this will find all descendants. Without, it will only include
        direct children.

        The order is by ID at each level::

            b
            a
              a     becomes [a, a (inner), c, b]
              c
        """

        for k, v in sorted(list(self.items())):
            if isinstance(v, Task):
                yield v
            if recurse and isinstance(v, Category):
                yield from v.tasks(True)

    def total_mins(self, recurse=True):
        """Sum of time in all tasks.

        With recurse, this includes all descendant tasks. Without, it includes only
        tasks directly inside this category.

        Tasks with `mins` set to zero are not counted in the sum.
        """

        return sum(t.mins or 0 for t in self.tasks(recurse))

    def delete(self, recurse=False):
        """Delete category.

        Refuse to delete categories containing sub-items unless `recurse` is true.
        """

        if self.__parent__ is None:
            raise Exception("Cannot delete category without parent")

        if self.keys() and not recurse:
            raise Exception(
                "Cannot delete Category {} without deleting children".format(self.id))

        del self.__parent__[self.id]


class Task(Persistent):
    """Task with times."""

    def __init__(self, id, title, description="", mins=None, parent=None):
        """Add a task."""

        if mins is not None and not isinstance(mins, int):
            raise ValueError("Task mins must be None or an integer")

        super().__init__()

        self.__parent__ = parent

        self.id = id
        self.title = title
        self.description = description
        self.mins = mins

    @property
    def __name__(self):
        """Required for traversal. Use the ID as the name."""

        return self.id

    def __repr__(self):
        return '<Task {} "{}">'.format(self.id, self.title)

    def delete(self):
        """Delete task."""

        if self.__parent__ is None:
            raise Exception("Cannot delete task without parent")

        del self.__parent__[self.id]
