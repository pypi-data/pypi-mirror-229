"""Defines the data types"""

from enum import Enum
from typing import NamedTuple, Dict, List


class Objective(Enum):
    """The routing objective"""

    MINIMIZE_TIME = "minimize travel time"
    MINIMIZE_DISTANCE = "minimize travel distance"
    MAXIMIZE_DELIVERIES = "maximize number of orders delivered"


class Vehicle(NamedTuple):
    """The data structure that contains vehicle information"""

    name: str  # The name of the vehicle
    shift_start: int  # The departure time of the vehicle (in minutes), 0 if non-applicable
    shift_end: int  # The return deadline of the vehicle (in minutes), 0 if non-applicable
    break_start: int  # The start time of the break (in minutes), 0 if non-applicable
    break_end: int  # The end time of the break (in minutes), 0 if non-applicable
    capacity: int  # The capacity of the vehicle, 0 if non-applicable


class Route:
    """Contains information of a route

    Attributes:
        route: The list of order IDs of locations visited
        departure: Time of departure from the depot
        return_time: Time of returning to the depot
        arrival_times: The arrival times at each order
        travel_time: The total travel time excluding wait times and service times
        travel_distance: The total travel distance
        trip_duration: The total duration of the trip

    """

    def __init__(
            self,
            route: List[int],
            departure: int,
            return_time: int,
            arrival_times: List[int],
            travel_time: int,
            travel_distance: int,
            **_
    ):
        self.route = route
        self.departure = departure
        self.return_time = return_time
        self.arrival_times = arrival_times
        self.travel_time = travel_time
        self.travel_distance = travel_distance
        self.trip_duration = self.return_time - self.departure

    def __str__(self):
        # Determine width of the first column
        order_id_len = max(len(str(order)) for order in self.route)
        first_column_len = max(10, order_id_len)
        res = "order_id".rjust(first_column_len, " ")

        # Finish header row
        res += "   arrival_time\n"
        res += "\n".rjust(len(res), "-")

        # Add the rest of the rows
        for order, time in zip(self.route, self.arrival_times):
            hour, minute = time // 60, time % 60
            res += f'{order:<{first_column_len}d}       {hour:02}:{minute:02}\n'

        # Add statistics
        res += f"\nDeparture Time: {self.departure} min"
        res += f"\nReturn Time: {self.return_time} min"
        res += f"\nNumber of orders served: {len(self.route)}"
        res += f"\nTotal Travel Time: {self.travel_time} min"
        res += f"\nTotal Distance Travelled: {self.travel_distance / 1000:.2f} km"
        hour, minute = self.trip_duration // 60, self.trip_duration % 60
        res += f"\nTrip Duration: {hour:02}h{minute:02}min"
        return res

    def to_dict(self):
        return vars(self)

    @classmethod
    def from_dict(cls, dict_obj: Dict):
        return cls(**dict_obj)
