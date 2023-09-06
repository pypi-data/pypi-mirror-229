from decimal import Decimal
from typing import Dict
from analysis.form_rating import FormRating
from analysis.race_conditions import RaceConditions


class FormPredictor:
    """
    A class for predicting form ratings for a race using current race conditions and past performance.
    """

    def __init__(self, race_conditions: RaceConditions):
        self.race_conditions = race_conditions

    def predict(
        self, past_performances: Dict[RaceConditions, FormRating]
    ) -> FormRating:
        weightings_and_ratings = [
            (self.race_conditions.similarity_to(key), value)
            for key, value in past_performances.items()
        ]

        numerator = sum(
            [
                Decimal(weighting) * rating.solidity * rating
                for weighting, rating in weightings_and_ratings
            ]
        )
        denominator = sum(
            [
                Decimal(weighting) * rating.solidity
                for weighting, rating in weightings_and_ratings
            ]
        )

        return FormRating(
            numerator / denominator,
            solidity=min(Decimal(denominator / 5), Decimal("1")),
        )
