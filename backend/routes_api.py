from fastapi import APIRouter, Query
import pandas as pd

router = APIRouter()

# Load GTFS static files
stops_df = pd.read_csv("stops.txt")
routes_df = pd.read_csv("routes.txt")
trips_df = pd.read_csv("trips.txt")
stop_times_df = pd.read_csv("stop_times.txt")

@router.get("/routes")
def list_routes():
    return sorted(routes_df['route_id'].unique().tolist())

@router.get("/stops-for-route")
def get_stops_for_route(route: str = Query(...)):
    # Get all trips for the given route
    trip_ids = trips_df[trips_df['route_id'] == route]['trip_id'].unique()

    # Get stop sequences for all those trips
    route_stop_times = stop_times_df[stop_times_df['trip_id'].isin(trip_ids)]

    # Choose the most common trip (usually represents the full route)
    trip_counts = route_stop_times['trip_id'].value_counts()
    top_trip_id = trip_counts.idxmax()
    stops_on_trip = route_stop_times[route_stop_times['trip_id'] == top_trip_id]
    stops_on_trip = stops_on_trip.sort_values('stop_sequence')

    stop_list = []
    for stop_id in stops_on_trip['stop_id'].unique():
        # Get stop name
        stop_name_row = stops_df[stops_df['stop_id'] == stop_id]
        if stop_name_row.empty:
            continue
        stop_name = stop_name_row.iloc[0]['stop_name']

        # Find other routes that serve this stop
        trips_with_this_stop = stop_times_df[stop_times_df['stop_id'] == stop_id]['trip_id'].unique()
        routes_at_stop = trips_df[trips_df['trip_id'].isin(trips_with_this_stop)]['route_id'].unique()
        other_routes = sorted([r for r in routes_at_stop if r != route])

        stop_list.append({
            "stop_id": stop_id,
            "stop_name": stop_name,
            "other_routes": other_routes
        })

    return {
        "route": route,
        "stops": stop_list
    }