# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shapeless']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'shapeless',
    'version': '0.0.2',
    'description': 'Poly - Pytorch',
    'long_description': "[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Poly\nA simple Fluid, PolyMorhic,and shapeless package that activates radically flexiblity and simplicity in your programs\n\n-----\n\n## Installation\n\nYou can install the package using pip\n\n```bash\npip install shapeless\n```\n----\n\n# Usage\n\nHere's a simple example of how to use the\xa0`Poly`\xa0class:\n\n```python\nfrom shapeless import Poly\n\n# Create a Poly object with an integer\np = Poly(10)\n\n# Determine the type of the data\nprint(p.determine())  # <class 'int'>\n\n# Shift the data to a string\nprint(p.shift(str))  # '10'\n\n# Validate that the data is a string\nprint(p.validate(str))  # True\n```\n\nYou can also use\xa0`Poly`\xa0as a type hint in your functions:\n\n```python\nfrom shapeless import Poly\n\ndef my_func(a: Poly):\n    print(type(a))\n\n# Create a Poly object with a string\np = Poly('10')\n\n# Pass the Poly object to my_func\nmy_func(p)  # <class '__main__.Poly'>\n```\n------\n\n# Documentation\nThe\xa0`Poly`\xa0class provides the following methods:\n\n-   `determine()`: Determine the type of the data.\n-   `select(target)`: Select the type of the data.\n-   `shift(target)`: Attempt to shift the data to the target type.\n-   `validate(target)`: Validate that the data is of the target type.\n-   `add_alias(alias, target)`: Add an alias for a type.\n-   `annotate(annotation)`: Annotate the data with a type.\n-   `extend(extension)`: Extend the type of the data with a new type.\n-   `serialize()`: Serialize the data.\n-   `deserialize(serialized_data)`: Deserialize the data.\n\n-----\n\n# Vision\nIn today's world, programming languages are often divided into statically-typed and dynamically-typed. While statically-typed languages provide type safety and performance benefits, they often lack the flexibility and simplicity that dynamically-typed languages offer. This has led to a growing demand for tools that can bring the benefits of both worlds together.\n\nWe believe the future of programming lies in the ability to handle types in a fluid and flexible manner, without sacrificing the benefits of static typing. However, achieving this is not easy. It requires a deep understanding of both static and dynamic typing, as well as the ability to create a tool that is easy to use, performant, and thread-safe.\n\nMany have tried to solve this problem, but none have succeeded. The challenge lies in creating a tool that is both powerful and simple to use. It requires a radical new approach, one that is not constrained by the traditional boundaries of static and dynamic typing.\n\nThat's where Poly comes in. Our secret is our deep understanding of the problems with static types. As creators of multi-modality and fluid intelligences with no defined shape, we have the unique insight and expertise needed to solve this problem. We have created a tool that allows you to handle dynamic types in a flexible and thread-safe manner, without sacrificing the benefits of static typing.\n\nWe are confident that Poly is the best solution to this problem. With our unique approach and deep expertise, we are perfectly positioned to bring this vision to life. Join us on this journey and experience the future of programming today.\n\nContribute Now\n\n\n-----\n\n\n# License\nMIT\n\n",
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/Poly',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
