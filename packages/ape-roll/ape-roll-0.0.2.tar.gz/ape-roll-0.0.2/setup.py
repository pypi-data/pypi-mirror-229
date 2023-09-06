# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ape_roll']

package_data = \
{'': ['*']}

install_requires = \
['eth-ape>=0.6.18,<0.7.0']

setup_kwargs = {
    'name': 'ape-roll',
    'version': '0.0.2',
    'description': 'Build weiroll transactions with ape',
    'long_description': "# ape-roll\n\n![April O'Neil](https://github.com/fp-crypto/ape-roll/assets/83050944/385dbc06-b9cb-4a80-89bf-72552f0e6d74)\n\nape-roll is a planner for the operation-chaining/scripting language [weiroll](https://github.com/weiroll/weiroll).\nape-roll is inspired by [weiroll.js](https://github.com/weiroll/weiroll.js).\n\nIt provides an easy-to-use API for generating weiroll programs that can then be passed to any compatible implementation.\n\n## Installation\n\n```\npip install ape-roll==0.0.2\n```\n\nwhere `0.0.2` is the latest version.\n\n## Usage\n\n### Wrapping contracts\nWeiroll programs consist of a sequence of calls to functions in external contracts. These calls can either be delegate calls to dedicated library contracts, or standard/static calls to external contracts. Before you can start creating a weiroll program, you will need to create interfaces for at least one contract you intend to use.\n\nThe easiest way to do this is by wrapping ape contract instances:\n\n```python\nape_contract = ape.Contract(address)\ncontract = ape_roll.WeirollContract(\n  ape_contract\n)\n```\n\nThis will produce a contract object that generates delegate calls to the ape contract in `WeirollContract`.\n\nTo create delegate to an external contract, use `createLibrary`:\n\n```python\nape_contract = ape.Contract(address)\n# Makes calls using CALL\ncontract = ape_roll.WeirollContract.createContract(ape_contract)\n# Makes calls using STATICCALL\ncontract = ape_roll.WeirollContract.createLibrary(ape_contract)\n```\n\nYou can repeat this for each contract you wish to use. A weiroll `WeirollContract` object can be reused across as many planner instances as you wish; there is no need to construct them again for each new program.\n\n### Planning programs\n\nFirst, instantiate a planner:\n\n```python\nplanner = ape_roll.WeirollPlanner()\n```\n\nNext, add one or more commands to execute:\n\n```python\nret = planner.add(contract.func(a, b))\n```\n\nReturn values from one invocation can be used in another one:\n\n```python\nplanner.add(contract.func2(ret))\n```\n\nRemember to wrap each call to a contract in `planner.add`. Attempting to pass the result of one contract function directly to another will not work - each one needs to be added to the planner!\n\nFor calls to external contracts, you can also pass a value in ether to send:\n\n```python\nplanner.add(contract.func(a, b).withValue(c))\n```\n\n`withValue` takes the same argument types as contract functions, so you can pass the return value of another function, or a literal value. You cannot combine `withValue` with delegate calls (eg, calls to a library created with `Contract.newLibrary`) or static calls.\n\nLikewise, if you want to make a particular call static, you can use `.staticcall()`:\n\n```python\nresult = planner.add(contract.func(a, b).staticcall())\n```\n\nWeiroll only supports functions that return a single value by default. If your function returns multiple values, though, you can instruct weiroll to wrap it in a `bytes`, which subsequent commands can decode and work with:\n\n```python\nret = planner.add(contract.func(a, b).rawValue())\n```\n\nOnce you are done planning operations, generate the program:\n\n```python\ncommands, state = planner.plan()\n```\n\n### Subplans\nIn some cases it may be useful to be able to instantiate nested instances of the weiroll VM - for example, when using flash loans, or other systems that function by making a callback to your code. The weiroll planner supports this via 'subplans'.\n\nTo make a subplan, construct the operations that should take place inside the nested instance normally, then pass the planner object to a contract function that executes the subplan, and pass that to the outer planner's `.addSubplan()` function instead of `.add()`.\n\nFor example, suppose you want to call a nested instance to do some math:\n\n```python\nsubplanner = WeirollPlanner()\nsum = subplanner.add(Math.add(1, 2))\n\nplanner = WeirollPlanner()\nplanner.addSubplan(Weiroll.execute(subplanner, subplanner.state))\nplanner.add(events.logUint(sum))\n\ncommands, state = planner.plan()\n```\n\nSubplan functions must specify which argument receives the current state using the special variable `Planner.state`, and must take exactly one subplanner and one state argument. Subplan functions must either return an updated state or nothing.\n\nIf a subplan returns updated state, return values created in a subplanner, such as `sum` above, can be referenced in the outer scope, and even in other subplans, as long as they are referenced after the command that produces them. Subplans that do not return updated state are read-only, and return values defined inside them cannot be referenced outside them.\n\n## More examples\n\nReview [tests](/tests) for more examples.\n\n## Credits\n\n- [@WyseNynja](https://github.com/WyseNynja) for the original implementation\n",
    'author': 'FP',
    'author_email': 'fp@noemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fp-crypto/ape-roll',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
