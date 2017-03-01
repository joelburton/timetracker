"""Utilities to "slugify" a string.

Slugifying replaces non-alphanumeric-or-dash characters with a single dash,
and lowercases the test. This is useful for creating attractive IDs from a
human-given title.
"""

import re

SLUGIFY_RE = re.compile(r"([^A-Za-z0-9]+)")


def slugify(s):
    """Turn string into slug.

        >>> slugify("Hello Joel")
        'hello-joel'

        >>> slugify("Hello, , Joel")
        'hello-joel'

        >>> slugify(" Hello ")
        'hello'
    """

    return SLUGIFY_RE.sub("-", s).lower().strip('-')


def slugify_unique(s, used):
    """Make a slug, ensuring it is unique among `used`.

    This slugifies text:

        >>> slugify_unique("Hello Joel", [])
        'hello-joel'

    If the slug that would be made it already present in `used`, increasingly-sized
    numbers are added after it. (Note that numbers start with "-2", not "-1", as users
    sometimes assume that "hello-1" would be the *first* "hello-" in a folder)

        >>> slugify_unique("Hello", ['hello'])
        'hello-2'

        >>> slugify_unique("Hello", ['hello', 'hello-2'])
        'hello-3'
    """

    prefix = slug = slugify(s)
    count = 1

    while slug in used:
        count += 1
        slug = f"{prefix}-{count}"

    return slug
