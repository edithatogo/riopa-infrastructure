"""YAML loading helpers with isolated YAML 1.2 boolean behaviour.

PyYAML's default resolver follows YAML 1.1 for several scalars (for example,
``yes``/``no``), and resolver tables are mutable class state.  RIOPA uses a
private loader subclass with copied resolver tables so importing this module
cannot mutate global ``yaml.safe_load`` behaviour.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

import yaml


class YAML12SafeLoader(yaml.SafeLoader):
    """Safe loader that recognises only true/false as implicit booleans.

    Timestamps are kept as strings because source registries and provenance
    records are validated as JSON-compatible documents after loading.
    """


YAML12SafeLoader.yaml_implicit_resolvers = copy.deepcopy(yaml.SafeLoader.yaml_implicit_resolvers)

for first_character, resolvers in list(YAML12SafeLoader.yaml_implicit_resolvers.items()):
    YAML12SafeLoader.yaml_implicit_resolvers[first_character] = [
        (tag, pattern)
        for tag, pattern in resolvers
        if tag not in {"tag:yaml.org,2002:bool", "tag:yaml.org,2002:timestamp"}
    ]

YAML12SafeLoader.add_implicit_resolver(  # type: ignore[no-untyped-call]
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)


def load_yaml(path: str | Path) -> Any:
    """Load a UTF-8 YAML file without mutating PyYAML's global loader state."""

    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.load(handle, Loader=YAML12SafeLoader)  # nosec B506 - SafeLoader subclass
