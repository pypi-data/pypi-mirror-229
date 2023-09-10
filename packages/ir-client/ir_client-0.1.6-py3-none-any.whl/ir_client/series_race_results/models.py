from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class SeriesRaceClassResult:
    car_class_id: int
    field_size: int
    strength_of_field: int

@dataclass
class SeriesRaceResult:
    subsession_id: int
    total_field_size: int
    split: int
    classes: dict[int, SeriesRaceClassResult]


@dataclass
class SeriesRaceResultsSlot:
    results: list[SeriesRaceResult] = field(default_factory=lambda: [])


@dataclass
class SeriesRaceResultCollection:
    slots: dict[datetime, SeriesRaceResultsSlot]
