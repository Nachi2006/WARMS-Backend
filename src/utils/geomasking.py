import math
import random

EARTH_RADIUS_KM = 6371.0
MASK_RADIUS_KM = 5.0

def apply_geomasking(latitude: float, longitude: float) -> tuple[float, float]:
    distance = random.uniform(0, MASK_RADIUS_KM)
    bearing = random.uniform(0, 2 * math.pi)

    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)
    angular_distance = distance / EARTH_RADIUS_KM

    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance)
        + math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing)
    )
    new_lon_rad = lon_rad + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat_rad),
    )

    return round(math.degrees(new_lat_rad), 6), round(math.degrees(new_lon_rad), 6)
