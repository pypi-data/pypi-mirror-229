from horsetalk import RaceConditions as HorsetalkRaceConditions  # type: ignore
from analysis.similarity import Similarity


class RaceConditions(HorsetalkRaceConditions):
    def similarity_to(self, other: "RaceConditions") -> float:
        return (
            Similarity.datetime(self.datetime, other.datetime)
            * self.distance.similarity_to(other.distance)
            * self.going.similarity_to(other.going)
            * Similarity.surface(self.surface, other.surface)
        )
