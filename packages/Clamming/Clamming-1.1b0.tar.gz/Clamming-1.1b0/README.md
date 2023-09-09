# Clamming - Light Python-API Documentation in markdown and html

## Overview

Clamming means fishing the seashells "clams" on a beach. Here we're 
fishing the documentation in a python source code...

Clamming is a simple library useful to convert a python `class` into 
a markdown or html file, for documentation purpose. The `Vehicle` sample 
is illustrating the supported format.

Notice that we expect to generate HTML-5 with WCAG 2.1 conformity, 
however it was not verified.


## Author

Copyright (C) 2023 - Brigitte Bigi - <develop@sppas.org>
Laboratoire Parole et Langage, Aix-en-Provence, France


## License

This is the implementation of the `Clamming` library, under the terms of
the GNU General Public License version 3.


## Install Clamming

### From clamming repo:

Download the repository and unpack it.
Clamming package includes the following folders and files:

1. "clamming": the source code folder
2. "docs": the documentation of clamming in HTML
3. "tests": unittest of clamming source code
4. "sample": includes a sample class `Vehicle` to illustrate `clamming` use
5. "sample.py": an example of use
6. "makedoc.py": create the Clamming documentation, using Clamming library
7. "etc": etcetera!

Take a look at the sample.py and makedoc.py files.


### From clamming package:

Install it in your python environment from the local wheel with:

```bash
> python -m pip install dist/<clamming.whl>
````


# Example of use

```python
>>> import clamming
>>> import Vehicle  # Any python class to be documented
>>> cp = clamming.ClammingParser(Vehicle)
>>> clams = ClamsClass(cp)
>>> print(clams.html())
>>> print(clams.markdown())
```

See Clamming documentation for extended usages.


## Projects using `Clamming`

- Clamming
- SPPAS <http://sppas/org> (asap...)
- *contact the author if you want to add a project here*
