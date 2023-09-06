from horsetalk import RaceDistance as HorsetalkRaceDistance  # type: ignore


class RaceDistance(HorsetalkRaceDistance):
    def __getattr__(self, name):
        if not name == "similarity_to":
            return super().__getattr__(name)

    def similarity_to(self, other: "RaceDistance") -> float:
        """
        Returns a similarity score between 0 and 1, where 1 is identical distances and 0 is the larger distance
        being > 1.5 times the smaller distance.

        Args:
            other: Another RaceDistance object.

        Returns:
            A similarity score between 0 and 1.
        """
        diff = abs(self.furlong - other.furlong)
        lower = min(self.furlong, other.furlong)
        proportion = float(diff / lower)
        similarity = 1 - ((proportion / 1.5) ** 0.5)
        return max(similarity, 0)
