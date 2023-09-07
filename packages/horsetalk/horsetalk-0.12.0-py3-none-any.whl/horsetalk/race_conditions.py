from pendulum import DateTime
from .going import Going
from .race_distance import RaceDistance
from .stalls_position import StallsPosition
from .racecourse import Racecourse


class RaceConditions:
    """
    A class for grouping together race conditions into a single object.

    """

    def __init__(
        self,
        *,
        datetime: DateTime,
        racecourse: Racecourse,
        distance: RaceDistance,
        going: Going,
        stalls_position: StallsPosition | None = None,
    ):
        """
        Initialize a RaceConditions instance.

        Args:
            datetime: The datetime of the race
            distance: The race distance
            going: The going of the race
            surface: The surface on which the race is run

        """
        self.datetime = datetime
        self.racecourse = racecourse
        self.distance = distance
        self.going = going
        self.stalls_position = stalls_position
