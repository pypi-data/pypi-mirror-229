"""Utility functions for the VRP module"""

from typing import Dict, List

import pandas as pd
from pandas import DataFrame

from foreqast.vrp.data_types import Vehicle


def load_orders(file_name: str) -> DataFrame:
    """Reads the file containing orders"""

    df = pd.read_excel(
        file_name,
        index_col=0,
        converters={
            'coordinates': eval
        }
    )

    orders = df[['coordinates']].copy()

    if 'date' in df.columns:
        orders['date'] = df['date']

    if 'tw_start' in df.columns:
        orders['tw_start'] = df['tw_start'].map(str).map(__convert_time_to_minutes)
        orders['tw_end'] = df['tw_end'].map(str).map(__convert_time_to_minutes)

    if 'service_time' in df.columns:
        orders['service_time'] = df['service_time'].map(lambda x: 0 if pd.isna(x) else int(x))

    if 'load' in df.columns:
        orders['load'] = df['load'].map(lambda x: 0 if pd.isna(x) else int(x))

    return orders


def load_vehicles(file_name: str) -> Dict[str, Vehicle]:
    """Reads the file containing vehicle information"""

    df = pd.read_excel(file_name)

    if 'Shift Start' not in df.columns:
        df['Shift Start'] = 0
        df['Shift End'] = 0
    else:
        df['Shift Start'] = df['Shift Start'].map(str).map(__convert_time_to_minutes)
        df['Shift End'] = df['Shift End'].map(str).map(__convert_time_to_minutes)

    if 'Break Start' not in df.columns:
        df['Break Start'] = 0
        df['Break End'] = 0
    else:
        df['Break Start'] = df['Break Start'].map(str).map(__convert_time_to_minutes)
        df['Break End'] = df['Break End'].map(str).map(__convert_time_to_minutes)

    if 'Capacity' not in df.columns:
        df['Capacity'] = 0
    else:
        df['Capacity'] = df['Capacity'].map(int)

    vehicles = {}
    for _, row in df.iterrows():
        vehicles[row['Vehicle']] = Vehicle(
            row['Vehicle'],
            row['Shift Start'],
            row['Shift End'],
            row['Break Start'],
            row['Break End'],
            row['Capacity']
        )

    return vehicles


def __convert_time_to_minutes(time: str) -> int:
    return 0 if pd.isna(time) else int(time[:-2]) * 60 + int(time[-2:])


def get_coordinates(client, address: str):
    """Gets the coordinates of an address in lng, lat format"""
    result = client.request(
        "GET", f"/map-services/get-coordinates", {"address": address})
    return result['coordinates']


def compute_adj_matrices(client, indices: List, coordinates: List):
    """Gets the travel time matrix and travel distance matrix"""
    body = client.request(
        "POST", f"/map-services/adj-matrices", {
            "indices": indices,
            "coordinates": coordinates
        })
    time_matrix = pd.read_json(body['time_matrix'], orient='split')
    distance_matrix = pd.read_json(body['distance_matrix'], orient='split')
    return time_matrix, distance_matrix
