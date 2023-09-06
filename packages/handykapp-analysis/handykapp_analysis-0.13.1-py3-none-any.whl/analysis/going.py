from typing import Self
from horsetalk import Going as HorsetalkGoing  # type: ignore


class Going(HorsetalkGoing):
    """
    A class to represent a going, wrapping the horsetalk class of the same name.
    """

    SIMILARITY_DIFFERENCE_PER_POINT = 0.125

    def similarity_to(self, other: Self) -> float:
        """
        Determine the similarity between this going and another going.

        Args:
            other: The other going.

        Returns:
            The similarity between this going and the other going.
        """
        return (
            1 - (abs(self.value - other.value) * Going.SIMILARITY_DIFFERENCE_PER_POINT)
            if self.value and other.value
            else 0
        )
