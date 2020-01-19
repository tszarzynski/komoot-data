import math

import gpxpy
import haversine
import pandas as pd
from geopy import distance

import utils

gpx_files_list = utils.get_file_list_by_ext('gpx')
FILES_LEN = 1  # len(gpx_files_list)
MOVEMENT_THRESHOLD = 0.6


def points_to_df(data):
    """ Convert GPX points to DataFrame """
    df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
    for point in data:
        df = df.append({'lon': point.longitude,
                        'lat': point.latitude,
                        'alt': point.elevation,
                        'time': point.time}, ignore_index=True)
    return df


def process_points(data):
    alt_dif = []
    time_dif = []
    dist_vin = []
    dist_hav = []
    dist_vin_no_alt = []
    dist_hav_no_alt = []
    dist_dif_hav_2d = []
    dist_dif_vin_2d = []

    for start, stop in zip(data[0::], data[1::]):

        distance_vin_2d = distance.geodesic(
            (start.latitude, start.longitude), (stop.latitude, stop.longitude)).m
        dist_dif_vin_2d.append(distance_vin_2d)

        distance_hav_2d = haversine.haversine(
            (start.latitude, start.longitude), (stop.latitude, stop.longitude))*1000
        dist_dif_hav_2d.append(distance_hav_2d)

        dist_vin_no_alt.append(
            (dist_vin_no_alt[-1] if len(dist_vin_no_alt) > 0 else 0) + distance_vin_2d)
        dist_hav_no_alt.append(
            (dist_hav_no_alt[-1] if len(dist_hav_no_alt) > 0 else 0) + distance_hav_2d)

        alt_d = start.elevation - stop.elevation

        alt_dif.append(alt_d)

        distance_vin_3d = math.sqrt(distance_vin_2d**2 + (alt_d)**2)

        distance_hav_3d = math.sqrt(distance_hav_2d**2 + (alt_d)**2)

        time_delta = (stop.time - start.time).total_seconds()

        time_dif.append(time_delta)

        dist_vin.append((dist_vin[-1] if len(dist_vin)
                         > 0 else 0) + distance_vin_3d)
        dist_hav.append((dist_hav[-1] if len(dist_hav)
                         > 0 else 0) + distance_hav_3d)

    # print('Vincenty 2D : ', dist_vin_no_alt[-1])
    # print('Haversine 2D : ', dist_hav_no_alt[-1])
    # print('Vincenty 3D : ', dist_vin[-1])
    # print('Haversine 3D : ', dist_hav[-1])
    # print('Total Time : ', math.floor(sum(time_dif)/60),
    #       ' min ', int(sum(time_dif) % 60), ' sec ')
    # print('Elevation diff: ', int(sum(alt_dif)))
    # print('Elevation loss: ', abs(int(sum([a for a in alt_dif if a > 0]))))
    # print('Elevation gain: ', abs(int(sum([a for a in alt_dif if a < 0]))))

    df = pd.DataFrame()
    df['dis_vin_2d'] = dist_vin_no_alt
    df['dist_hav_2d'] = dist_hav_no_alt
    df['dis_vin_3d'] = dist_vin
    df['dis_hav_3d'] = dist_hav
    df['alt_dif'] = alt_dif
    df['time_dif'] = time_dif
    df['dis_dif_hav_2d'] = dist_dif_hav_2d
    df['dis_dif_vin_2d'] = dist_dif_vin_2d

    # Clear data set
    df = df[df['time_dif'] > 0.0]

    df['dist_dif_per_sec'] = df['dis_dif_hav_2d'] / df['time_dif']
    df['spd'] = (df['dis_dif_hav_2d'] / df['time_dif']) * 3.6

    df_with_timeout = df[df['dist_dif_per_sec'] > MOVEMENT_THRESHOLD]

    avg_km_h = (sum((df_with_timeout['spd'] *
                     df_with_timeout['time_dif'])) /
                sum(df_with_timeout['time_dif']))

    # print(math.floor(60 / avg_km_h), 'minutes',
    #       round(((60 / avg_km_h - math.floor(60 / avg_km_h))*60), 0),
    #       ' seconds')

    return {'dist': dist_hav_no_alt[-1],
            'total_time': math.floor(sum(time_dif)),
            'moving_time': sum(df_with_timeout['time_dif']),
            'alt_loss': abs(int(sum([a for a in alt_dif if a > 0]))),
            'alt_gain': abs(int(sum([a for a in alt_dif if a < 0]))),
            'avg_km_h': avg_km_h}


def main(write_to_file=False):
    print('Processing %d files.' % (FILES_LEN))
    df = pd.DataFrame()
    for index, filename in zip(range(FILES_LEN), gpx_files_list):
        gpx_file = open(filename)
        gpx = gpxpy.parse(gpx_file)
        data = gpx.tracks[0].segments[0].points
        print('>>> Track: ', gpx.tracks[0].name)
        df = df.append(process_points(data), ignore_index=True)

    print(df)
    if write_to_file:
        df.to_json('processed.json', orient='index')


main()
