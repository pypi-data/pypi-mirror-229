from setuptools import setup,  find_namespace_packages

VERSION = '0.1.2'
DESCRIPTION = 'Import python module using url with importurl'
ld = """
# ImportURL

[![Discord][1]](<https://discord.com/channels/267624335836053506/>)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Hello, From python discord server

## What is importurl ?

importurl is a python module to import python modules using url

### Example

```python
import importurl
example_module = importurl.Module ("https://example.com/module.py")
```

### Documentations

Docs included with markdown format in docs folder

## My profile in python discord server

![AVATAR](https://avatars.githubusercontent.com/u/136630721?v=4)

@Giga Coder

[1]: https://raw.githubusercontent.com/python-discord/branding/main/logos/badge/badge_github.svg

"""
setup (
    name="importurl",
    version=VERSION,
    author="VenzTechnolo",
    author_email="venztechnolo@gmail.com",
    description=DESCRIPTION,
    long_description=ld,
    requires=["requests"],
    include_package_data=True,
    packages=find_namespace_packages(),
    package_data={"importurl" : ["*.pyi"]},
    py_modules=["module", "__init__"],
    keywords=["import", "module", "url", "requests"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable"
    ]
)
