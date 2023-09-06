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


    >>> f = mk_str_attr_obj('date worker offre success')
    >>> f.date
    'date'
    >>> f.worker
    'worker'
    >>> f.does_not_exist
    Traceback (most recent call last):
    ...
    AttributeError: 'AttrObj' object has no attribute 'does_not_exist'



