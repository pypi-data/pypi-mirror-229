from pendulum import DateTime
from .going import Going
from .race_distance import RaceDistance
from .stalls_position import StallsPosition
from .surface import Surface


class RaceConditions:
    """
    A class for grouping together race conditions into a single object.

    """

    def __init__(
        self,
        *,
        datetime: DateTime,
        distance: RaceDistance,
        going: Going,
        surface: Surface,
        stalls_position: StallsPosition = None,
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
        self.distance = distance
        self.going = going
        self.stalls_position = stalls_position
        self.surface = surface
