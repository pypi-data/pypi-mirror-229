import re
import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True, eq=True)
class Event:
    id: str = field(
        init=False,
        default_factory=lambda: str(uuid.uuid4()),
        repr=True
    )

    name: str = field(
        init=False,
        repr=True
    )

    def __init_subclass__(self):
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__name__)
        self.name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
