from dataclasses import dataclass, field
from pprint import pprint
from sys import version_info

default_version = (3, 10)
min_version = (3, 8)
cur_version = version_info
if cur_version >= default_version:
    _IDSPYDD_USE_SLOTS = True
elif cur_version >= min_version:
    _IDSPYDD_USE_SLOTS = False
else:
    raise ImportError('needs at least python==3.8, full support for python >=3.10')


@dataclass(slots=True)
class IdsBaseClass:
    """
        Base class used for all the IDS
    """

    @property
    def print_ids(self) -> object:
        """
            print IDS field values
        """
        pprint(f"current ids : {self}", indent=2)
        return None

    @property
    def slots_used(self) -> bool:
        """
            print IDS field values
        """
        return _IDSPYDD_USE_SLOTS