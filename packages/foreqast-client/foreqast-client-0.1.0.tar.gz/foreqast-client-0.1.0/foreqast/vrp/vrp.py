"""Functions related to the VRP."""

from typing import Dict, List

from pandas import DataFrame

from foreqast.vrp.data_types import Vehicle, Objective, Route
from foreqast.vrp.utils import get_coordinates, compute_adj_matrices

DEPOT_INDEX = 0


class VRP:
    """Container for problem definition and constraints

    Attributes:
        depot_address: The address of the depot
        depot_coordinates: The coordinates of the depot
        orders: The list of orders to plan routes for
        vehicles: The list of vehicles to plan routes for
        time_matrix: The travel time matrix
        distance_matrix: The travel distance matrix

    """

    def __init__(
            self,
            client,
            depot_address: str,
            orders: DataFrame,
            vehicles: Dict[str, Vehicle],
    ):
        self.client = client
        self.depot_address = depot_address
        self.depot_coordinates = get_coordinates(self.client, depot_address)
        self.orders = orders
        self.vehicles = vehicles

        indices = [DEPOT_INDEX] + orders.index.to_list()
        coordinates = [self.depot_coordinates] + orders['coordinates'].to_list()
        self.time_matrix, self.distance_matrix = compute_adj_matrices(
            self.client, indices, coordinates)

    def cluster(
            self,
            objective: Objective,
            vehicles: List[str] = None,
            balancing_alpha=0,
            use_quantum=True
    ):
        """Attach cluster assignments to the orders

        Args:
            objective: The objective of the routing
            vehicles: The vehicles used in clustering, use all vehicles by default
            balancing_alpha: The alpha value for balancing the clusters, typically between 0 and 8.
            use_quantum: Whether to use the quantum algorithm for the clustering

        """
        selected_vehicles = dict(
            (k, v) for k, v in self.vehicles.items()
            if vehicles is None or k in vehicles
        )
        bound_capacity = objective in (Objective.MINIMIZE_DISTANCE, Objective.MINIMIZE_TIME)
        body = self.client.request(
            "POST", "/vrp/cluster", {
                "orders": self.orders.to_json(orient='split'),
                "vehicles": selected_vehicles,
                "time_matrix": self.time_matrix.to_json(orient='split'),
                "balancing_alpha": balancing_alpha,
                "bound_capacity": bound_capacity,
                "use_quantum": use_quantum,
            }
        )
        self.orders = self.orders.assign(cluster=body['clusters'])

    def plan_routes(self, objective: Objective, vehicles: List[str] = None):
        """Plans the routes for each vehicle

        Args:
            objective: The objective of the routing
            vehicles: The list of vehicles to plan routes for, use all vehicles if not specified

        Returns:
            A dictionary containing the Route object generated for each vehicle

        """

        selected_vehicles = [
            v for k, v in self.vehicles.items()
            if k in self.orders['cluster'].unique() and (vehicles is None or k in vehicles)
        ]
        body = self.client.request(
            "POST", "/vrp/plan-routes", {
                "orders": self.orders.to_json(orient='split'),
                "vehicles": selected_vehicles,
                "time_matrix": self.time_matrix.to_json(orient='split'),
                "distance_matrix": self.distance_matrix.to_json(orient='split'),
                "objective": objective.name
            }
        )
        return dict((k, Route.from_dict(v)) for k, v in body['routes'].items())

    def solve_vrp(
            self,
            objective: Objective,
            vehicles: List[str] = None,
            balancing_alpha=0,
            use_quantum=True
    ):
        """Plans the routes for each vehicle

        Args:
            objective: The objective of the routing
            vehicles: The list of vehicles to plan routes for, use all vehicles if not specified
            balancing_alpha: The alpha value for balancing the clusters, typically between 0 and 8.
            use_quantum: Whether to use the quantum algorithm for the clustering

        Returns:
            A dictionary containing the Route object generated for each vehicle

        """

        selected_vehicles = dict(
            (k, v) for k, v in self.vehicles.items()
            if vehicles is None or k in vehicles
        )

        body = self.client.request(
            "POST", "/vrp/solve-vrp", {
                "orders": self.orders.to_json(orient='split'),
                "vehicles": selected_vehicles,
                "time_matrix": self.time_matrix.to_json(orient='split'),
                "distance_matrix": self.distance_matrix.to_json(orient='split'),
                "balancing_alpha": balancing_alpha,
                "bound_capacity": objective != Objective.MAXIMIZE_DELIVERIES,
                "objective": objective.name,
                "use_quantum": use_quantum
            }
        )
        self.orders = self.orders.assign(cluster=body['clusters'])
        return dict((k, Route.from_dict(v)) for k, v in body['routes'].items())
