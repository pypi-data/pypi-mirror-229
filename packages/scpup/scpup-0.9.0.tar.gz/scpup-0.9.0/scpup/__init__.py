"""scpup package contains the classes, constants, types, etc., needed in the
game SCPUP (Super Crystal Pokebros Ultimate Party).

Any exported member of any module within this package can be accessed from this
scope, for example to use the class EauSprite you could import it like this:

```python
from scpup import EauSprite
EauSprite()
# or
import scpup
scpup.EauSprite()
```

This package includes the following modules:

* service
* sprite
* group
* ctrl
* loader
* view
* player
* text
* time

For more information on a specific module, go to its documentation.
"""

from .service import *  # noqa
from .loader import *  # noqa
from .sprite import *  # noqa
from .group import *  # noqa
from .view import *  # noqa
from .player import *  # noqa
from .ctrl import *  # noqa
from .text import *  # noqa

__name__ = "scpup"
__package__ = "scpup"
