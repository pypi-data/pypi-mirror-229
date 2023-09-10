# readmint

[![PyPI - Version](https://img.shields.io/pypi/v/readmint.svg)](https://pypi.org/project/readmint)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/readmint.svg)](https://pypi.org/project/readmint)

* * *

A simple, yet effective way of adding some dynamic properties to you md. 

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install readmint
```

## Using it (shell)

## Using it (api)

```python
# import the render function

In [1]: from readmint.lib.renderer import render_text, render_file
        import textwrap

        print("hello world")
```

```python
# render text just rendera passed text
In [2]: render_text(
            textwrap.dedent("""
                dummy text
                ==========
        
                And this is a code block
        
                ```readmint[python@local]
                1+1
                ```
            """)
        )

Out[2]: 
# dummy text

And this is a code block

```python

In [1]: 1+1

Out[1]: 2
```
```

## License

`readmint` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
