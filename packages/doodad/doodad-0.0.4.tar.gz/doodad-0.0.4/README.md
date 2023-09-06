# doodad

Making access to names easier.

doodad: A gadget or other object whose name the speaker does not know or cannot recall.

Often, when writing code, you need to specify field names, for example, when writing code that 
communicates with a database. It's so easy to make a typo in the field name, and you might only know 
this once you run the code, which may be a lot later...

What `doodad` wants to do when it grows up, is make it easier to find names, and use the names 
you meant to use, with tab completion etc.

To install:	```pip install doodad```


# Examples

Find all the names (variables, functions, etc.) in a piece of code or data.

    >>> from doodad import find_names
    >>> mapping = {'c': 1, 'b': {'a': 2, 'd': 3}}
    >>> list(find_names(mapping))
    ['c', 'b', 'a', 'd']
    >>> import os
    >>> names = list(find_names(os.path.join))
    >>> names
    ['join', 'a', 'a', 'sep', 'path', 'path']


Make an instance whose sole purpose is to contain those names.
This allows you to have a ready-to-use collection of names that you can tab complete 
and catch spelling mistakes early (before, say, you ask for a field name that doesn't exist...)

    >>> from doodad import mk_str_attr_obj
    >>>
    >>> f = mk_str_attr_obj(names)
    >>> f.join
    'join'
    >>> f.path
    'path'
    >>> f = mk_str_attr_obj('date worker offre success')
    >>> f.date
    'date'
    >>> f.worker
    'worker'
    >>> f.does_not_exist
    Traceback (most recent call last):
    ...
    AttributeError: 'AttrObj' object has no attribute 'does_not_exist'

`f` is a `namedtuple` so you can do things like:

    >>> list(f)
    ['date', 'worker', 'offre', 'success']
    >>> date, worker, offer, success = f
    >>> offer
    'offre'

