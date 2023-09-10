# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dynamic_imports']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dynamic-imports',
    'version': '1.0.1',
    'description': 'Dynamically discover and import Python modules, classes, and functions.',
    'long_description': "# Dynamically discover and import Python modules, classes, and functions.\n\n## Install\n`pip install dynamic_imports`\n\n## Examples\n### Import a module via module name or file path\n```python\nfrom dynamic_imports import import_module\nmodule = import_module('my_package.my_module')\n# or\nmodule = import_module('/home/user/my_package/my_module.py')\n```\n### Import a module attribute\n```python\nfrom dynamic_imports import import_module_attr\n\nfunction = import_module_attr('my_package.my_module', 'my_function')\n# or\nfunction = import_module_attr('/home/user/my_package/my_module.py', 'my_function')\n```\n### Find all modules in a package or nested packages\n```python\nfrom dynamic_imports import discover_modules\n\nmodules = discover_modules(\n    package=my_package, # str `my_package' works too.\n    search_subpackages=True,\n    # return the actual module objects, not str names.\n    names_only=False,\n)\n\n```\n### Find all implementations of a base class within a module.\n```python\nfrom dynamic_imports import class_impls\nfrom my_package.my_module import Base\nfrom my_package import my_module\n\nmy_classes = class_impls(\n    base_class=Base, # str 'Base' works too\n    search_in=my_module,\n    names_only=False\n)\n```\n### Find all implementations of a base class within nested packages.\n```python\nfrom dynamic_imports import class_impls\nfrom my_package.my_module import Base\nimport my_package\n\nmy_classes = class_impls(\n    base_class=Base, # str 'Base' works too.\n    search_in=my_package\n    search_subpackages=True,\n    names_only=False,\n)\n\n```\n### Find all instances of a class within a module.\n```python\nfrom dynamic_imports import class_inst\nfrom my_package import my_module\nfrom my_package.my_module import MyClass\n\nmy_classes_instances = class_inst(\n    search_in=my_module, # str 'my_package.my_module' works too.\n    class_type=MyClass\n)\n```\n### Find all instances of a class within nested packages.\n```python\nfrom dynamic_imports import class_inst\nfrom my_package.my_module import MyClass\nimport my_package\n\nmy_classes_instances = class_inst(\n    class_type=MyClass,\n    search_in=my_package, # str 'my_package' works too.\n    search_subpackages=True,\n)\n```",
    'author': 'Dan Kelleher',
    'author_email': 'kelleherjdan@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/djkelleher/dynamic-imports',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8.1,<4.0.0',
}


setup(**setup_kwargs)
