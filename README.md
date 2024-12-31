# maya-zen-tools

[![test](https://github.com/davebelais/maya-zen-tools/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/davebelais/maya-zen-tools/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/maya-zen-tools.svg?icon=si%3Apython)](https://badge.fury.io/py/maya-zen-tools)

## Installation

You can install `maya-zen-tools` from the command line as follows, if `mayapy`
is in your system path:

```bash
mayapy -m pip install maya-zen-tools && mayapy -m maya_zen_tools.install
```

You can also install `maya-zen-tools` from you script editor in Maya
by executing the following:

```python
import sys
from subprocesses import check_call

check_call([sys.executable, "-m", "pip", "install", "maya-zen-tools"])
check_call([sys.executable, "-m", "maya_zen_tools.install"])

from maya_zen_tools import startup
```
