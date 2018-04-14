Introduction to dirstr
======================

This tool makes a directory structure according to a specifcation file (called
a `spec`). The idea is:

- take a directory root,
- take a `spec`,
- remove any nonmatching file or directory.

Matching files
--------------

Each file or directory (an item for short) is assigned a `category`. If a
category matches, the item is left, and if it does not, it is removed.

Any extra file in the directory root or the `spec` causes an error by default.
It is however possible to ignore missing files in the root directory under a
certain category, to allow working on an "incomplete" root directory.

Why
---

It has been created to manage certain "split packages" in the Sabayon GNU/Linux
distribution where it is needed to perform a cleanup of a directory according
to a file list, whilst performing strict checks to help not to miss anything
during a version bump. (At the moment of writing this way is still in
development.)

Status
------

Anything can change, although probably in a reasonably backwards compatible
manner.

Usage
-----

See `./dirstr.py --help`. For an example, see
`tests/already-missing-ignored-only-to_be_removed-files/run.sh`.

Running tests
-------------

Tests are in `tests`. Use one of:
- `./run-all.sh`,
- `./run-all.sh TEST_DIR [TEST_DIR ...]`.

Dependencies
------------

Python 3. It has been tested on 3.5 and 3.6, so it is safe to say
`Python 3.5+`. As for the previous Python 3 versions, run tests to find out.

Spec file format
----------------

    find . -depth | sed 's/^/<class><space>/'

`-depth` matters because no recursive removal is made but one item at a time,
in order.

Author and stuff
----------------

Copyright (C) 2018 by Sławomir Nizio.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
