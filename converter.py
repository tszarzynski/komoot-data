""" Convert GPX to GeoJSON and MBTiles """
import os
import togeojsontiles

TIPPECANOE_DIR = '/usr/local/bin/'


def to_geo_json():
    """ Convert GPX to GeoJSON """
    for file in get_file_list_by_ext('.gpx'):
        file_gpx = os.path.join("./data", file)
        file_geojson = os.path.join(
            "./data", os.path.splitext(file)[0] + '.geojson')
        togeojsontiles.gpx_to_geojson(
            file_gpx=file_gpx, file_geojson=file_geojson)


def to_mb_tiles():
    """ convert GeoJSON to MBTiles """
    togeojsontiles.geojson_to_mbtiles(
        filepaths=get_file_list_by_ext('.geojson'),
        tippecanoe_dir=TIPPECANOE_DIR,
        mbtiles_file='out.mbtiles',
    )


def get_file_list_by_ext(ext, dir="./data"):
    """ Get list of files by extension """
    return [os.path.join(dir, file) for file in os.listdir(dir) if file.endswith(ext)]
