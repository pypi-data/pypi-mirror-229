from typing import List, Set, Literal

from pydantic import Field

from api_compose.services.common.models.base import BaseModel
from api_compose.root.models.scenario import ScenarioModel


class SpecificationModel(BaseModel):
    scenarios: List[ScenarioModel]


    @property
    def is_success(self) -> bool:
        return all([scenario.is_success for scenario in self.scenarios])

    @property
    def elapsed_time(self) -> float:
        return sum(scenario.elapsed_time for scenario in self.scenarios)

