from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import datetime
import pandas as pd
import requests
from google.transit import gtfs_realtime_pb2


app = FastAPI()

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

# Load GTFS stop metadata
stops_df = pd.read_csv("stops.txt")

FEED_URLS = [
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"
]

def fetch_all_feeds():
    feeds = []
    for url in FEED_URLS:
        feed = gtfs_realtime_pb2.FeedMessage()
        resp = requests.get(url)
        feed.ParseFromString(resp.content)
        feeds.append(feed)
    return feeds

def get_arrivals_by_direction(station_name):
    feeds = fetch_all_feeds()
    stop_ids = stops_df[stops_df['stop_name'] == station_name]['stop_id'].tolist()
    arrivals = {"northbound": [], "southbound": []}
    now = datetime.datetime.now()

    for sid in stop_ids:
        direction = "northbound" if sid.endswith("N") else "southbound" if sid.endswith("S") else None
        if not direction:
            continue
        for feed in feeds:
            for entity in feed.entity:
                if entity.HasField("trip_update"):
                    route = entity.trip_update.trip.route_id
                    for stu in entity.trip_update.stop_time_update:
                        if stu.stop_id == sid:
                            t = stu.arrival.time if stu.HasField("arrival") else stu.departure.time
                            if t:
                                minutes = int((datetime.datetime.fromtimestamp(t) - now).total_seconds() / 60)
                                if minutes >= 0:
                                    arrivals[direction].append({"route": route, "minutes": minutes})
    return arrivals

@app.get("/arrivals")
def arrivals(station: str = Query(...)):
    return get_arrivals_by_direction(station)

@app.get("/stations")
def stations():
    return sorted(stops_df['stop_name'].unique().tolist())

from routes_api import router as routes_router
app.include_router(routes_router)