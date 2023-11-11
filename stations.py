import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pydantic import BaseModel

from stations_dao import fetch_stations
from stations_dao import fetch_stations_net


def show(network, graph):
    network.draw(graph, pos=nx.spring_layout(graph), node_size=2)
    plt.savefig("Graph.png", format="PNG")


class Station(BaseModel):
    id: int
    latitude: float
    longitude: float


class Edge(BaseModel):
    start: Station
    end: Station
    distance: float


# todo: broken fixme!
def find_stations(left, top, right, down):
    stations = {}
    for row in fetch_stations():
        station_id = row[0]
        latitude = row[1]
        longitude = row[2]
        if is_inside(left, top, right, down, longitude, latitude):
            stations[station_id] = Station(id=station_id, longitude=float(longitude), latitude=float(latitude))

    edges = []
    for row in fetch_stations_net():
        start_id = row[0]
        end_id = row[1]
        # todo: make sql instead of this
        if stations.keys().__contains__(start_id) and stations.keys().__contains__(end_id):
            edges.append(Edge(start=stations.get(start_id), end=stations.get(end_id), distance=row[2]))


# left, right - longitude
# top, down - latitude
def is_inside(left, top, right, down, point_longitude, point_latitude):
    return point_longitude != None and point_latitude != None and left > point_longitude and point_longitude < right and point_latitude > down and point_latitude < top;


def find_paths(start_station_id, end_station_id):
    stations = {}
    for row in fetch_stations():
        station_id = row[0]
        latitude = row[1]
        longitude = row[2]
        if latitude != None and longitude != None:
            stations[station_id] = Station(id=station_id, longitude=float(longitude), latitude=float(latitude))
        else:
            print(f"failed to init station: {station_id}")

    graph = nx.Graph()
    for row in fetch_stations_net():
        start = row[0]
        end = row[1]
        distance = row[2]
        graph.add_edge(start, end, distance=distance)

    try:
        edged_paths = []
        for simple_path in nx.all_simple_paths(graph, source=start_station_id, target=end_station_id):
            edged_path = []
            left = simple_path[0]
            for right in simple_path[1:]:
                distance = graph.get_edge_data(left, right)
                edged_path.append(Edge(
                    start=stations.get(left),
                    end=stations.get(right),
                    distance=distance['distance']
                ))

                left = right
            edged_paths.append(edged_path)

        return edged_paths

    except Exception as e:
        print(f"No paths. {e}")
        return {}


if __name__ == "__main__":
    find_paths(7741, 22294)
