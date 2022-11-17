import mercantile


def point_to_quadkey(lon: float, lat: float, zoom: int) -> str:
    tile = mercantile.tile(lon, lat, zoom)

    return mercantile.quadkey(tile)