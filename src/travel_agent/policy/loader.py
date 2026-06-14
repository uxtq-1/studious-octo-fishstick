"""Company travel policy loading."""

from pathlib import Path

import yaml

from travel_agent.policy.models import TravelPolicy


def load_policy(path: Path) -> TravelPolicy:
    with path.open(encoding="utf-8") as policy_file:
        data = yaml.safe_load(policy_file)
    return TravelPolicy.model_validate(data)
