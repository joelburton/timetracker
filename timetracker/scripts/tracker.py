"""Interface for time tracker administration.

If called without arguments, enters REPL mode. With an argument,
runs that single command.
"""

import sys
import cmd
import os
from functools import reduce
from pprint import pprint

import ZODB
import transaction

from timetracker.models import Category, Task
from timetracker.slugify import slugify_unique

INTRO = """

Time Tracker

You can use this to view, add, and delete categories and tasks.

`help` will show the available commands. Note that many commands
have a "recursive" form that acts recursively (for example,
`cats work` shows categories directly in the `work` category,
while `rcats work` shows all categories anywhere below `work`.

""".strip()


class TrackerCmd(cmd.Cmd):
    """REPL for time tracker administration."""

    prompt = "\ntracker> "
    intro = INTRO

    def __init__(self, *args, **kwargs):
        db_filename = kwargs.pop("database", "data.fs")
        super().__init__(*args, **kwargs)

        self.db = ZODB.connection(db_filename)
        self.root = self.db.root()

    def traverse(self, path_string):
        """Get an object given a dotted.path.string.

            >>> c = TrackerCmd(database=None)
            >>> c.root = {"b": {"c": "C"}}

            >>> c.traverse("")
            {'b': {'c': 'C'}}

            >>> c.traverse("b")
            {'c': 'C'}

            >>> c.traverse("b.c")
            'C'
        """

        path = (p for p in path_string.split(".") if p)
        obj = reduce(lambda a, b: a[b], path, self.root)
        return obj

    def do_ls(self, arg, recurse=False):
        """ls [path]: Directory of categories/tasks at path"""

        def ls(obj):
            for child in obj.values():
                pprint(child)
                if recurse and hasattr(child, 'values'):
                    ls(child)

        ls(self.traverse(arg))

    def do_rls(self, arg):
        """rls [path]: Recursive directory of categories/tasks at path"""

        self.do_ls(arg, recurse=True)

    def do_cats(self, arg, recurse=False):
        """cats [path]: Categories at path"""

        objs = [self.traverse(arg)]

        if objs == [self.root]:
            objs = self.root.values()

        for o in objs:
            pprint(list(o.categories(recurse=recurse)))

    def do_rcats(self, arg):
        """rcats [path]: Recursive categories at path"""

        self.do_cats(arg, recurse=True)

    def do_tasks(self, arg, recurse=False):
        """tasks [path]: Tasks at path"""

        objects = [self.traverse(arg)]

        if objects == [self.root]:
            if not recurse:
                return []
            else:
                objects = self.root.values()

        for o in objects:
            pprint(list(o.tasks(recurse=recurse)))

    def do_rtasks(self, arg):
        """rtasks [path]: Recursive tasks at path"""

        self.do_tasks(arg, recurse=True)

    def do_addcat(self, arg):
        """addcat [path]: Add a category at path"""

        parent = self.traverse(arg)
        title = input("Title: ")
        id = slugify_unique(title, parent.keys())
        new_id = input("ID [{}]: ".format(id))
        id = new_id or id
        description = input("Description: ")

        if parent is self.root:
            new = Category(id, title, description, parent=self.root)
            self.root[id] = new

        else:
            new = parent.add_category(title=title, id=id, description=description)

        pprint(str(new))

    def do_addtask(self, arg):
        """addtask [path]: Add task at path"""

        parent = self.traverse(arg)

        if not isinstance(parent, Category):
            raise ValueError("Can only add tasks to categories")

        title = input("Title: ")
        id = slugify_unique(title, parent.keys())
        new_id = input("ID [{}]: ".format(id))
        id = new_id or id
        description = input("Description: ")
        mins = input("Minutes: ")
        mins = int(mins) if mins else None

        new = parent.add_task(title=title, id=id, description=description, mins=mins)

        pprint(str(new))

    def do_total(self, arg, recurse=False):
        """total [path]: Total minutes of tasks at path"""

        obj = self.traverse(arg)
        if isinstance(obj, Task):
            print(obj.mins)

        elif isinstance(obj, Category):
            print(obj.total_mins(recurse=recurse))

        elif obj is self.root:
            if not recurse:
                print("0 [no tasks at root]")
            else:
                print(sum(c.total_mins(recurse=recurse) for c in self.root.values()))

    def do_rtotal(self, arg):
        """rtotal [path]: Total minutes of tasks recursively under path"""

        self.do_total(arg, recurse=True)

    def do_rm(self, arg, recurse=False):
        """rm [path]: Delete object at path"""

        obj = self.traverse(arg)

        if obj is self.root:
            raise ValueError("Cannot delete root")

        obj.delete(recurse=recurse)

    def do_rrm(self, arg):
        """rrm [path]: Delete object at path, recursively deleting children"""

        self.do_rm(arg, recurse=True)

    def do_edit(self, arg):
        """edit [path]: Edit object"""

        obj = self.traverse(arg)

        if obj is self.root:
            raise Exception("Cannot edit root")

        obj.title = input("Title: ")
        obj.description = input("Description: ")
        if isinstance(obj, Task):
            mins = input("Minutes: ")
            obj.mins = int(mins) if mins else None

    def emptyline(self):
        """On empty command, don't repeat former command -- do nothing."""

    def postcmd(self, stop, line):
        """After every command. commit database."""

        transaction.commit()
        return stop

    # noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
    def do_EOF(self, args):
        """Quit."""

        print("Goodbye!")
        return True

    def do_quit(self, args):
        """Quit."""

        return self.do_EOF(args)

    def postloop(self):
        """Exit cleanly."""

        self.db.close()


USAGE = """

Time Tracker Console App

usage:
    {program_name} <database>       for interactive mode
    {program_name} <database> cmd   for single command ("help" provides help)

For <database> you can provide a filename; it will be created if needed.

"""


def main():
    """Handle shell input.

    Requires a database name; confirms before creating a non-existent db.

    With no remaining arguments, enter interactive mode.
    Otherwise, concat args single string and use as one command for REPL.
    """

    program_name, *args = sys.argv

    if not args or "-h" in sys.argv or "--help" in sys.argv:
        program_name = os.path.basename(program_name)
        print(USAGE.strip().format(program_name=program_name))
        return

    database, *args = args

    if not os.path.exists(database):
        while True:
            yn = input("{} does not exist; create? (y/n) ".format(database))
            if yn.lower() in ["yes", "y"]:
                break
            elif yn.lower() in ["no", "n", "quit", "q"]:
                return

    tracker = TrackerCmd(database=database)

    if not args:
        tracker.cmdloop()

    else:
        arg = " ".join(args)
        tracker.onecmd(arg)
