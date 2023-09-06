from pendulum import DateTime
from horsetalk import Surface  # type: ignore


class Similarity:
    @staticmethod
    def datetime(date_1: DateTime, date_2: DateTime) -> float:
        """
        Returns a similarity score between 0 and 1, where 1 is identical dates and 0 is dates 1000 days apart.

        Args:
            date_1: The first date.
            date_2: The second date.

        Returns:
            A similarity score between 0 and 1.
        """
        days_delta = abs((date_1 - date_2).days)
        # similarity reaches 0 after 1000 days
        return max(1 - ((days_delta / 10) ** 0.5) / 10, 0)

    @staticmethod
    def surface(surface_1: Surface, surface_2: Surface) -> float:
        """
        Returns a similarity score between 0 and 1, where 1 is identical surface, 0.9 are different all-weather surfaces
        and 0.7 are different fundamental surfaces.

        Args:
            surface_1: The first surface.
            surface_2: The second surface.

        Returns:
            A similarity score between 0 and 1.
        """
        return (
            1
            if surface_1 == surface_2
            else 0.9
            if all(
                x in [Surface.FIBRESAND, Surface.POLYTRACK, Surface.TAPETA]
                for x in [surface_1, surface_2]
            )
            else 0.7
        )
