from dateutil import parser
import matplotlib.pyplot as plt
import gpxpy
import pandas as pd
import matplotlib
matplotlib.use('Agg')


gpx_file = open(
    'data/https-external-api-komoot-de-v007-tours-85473661-gpx.gpx', 'r')
gpx = gpxpy.parse(gpx_file)
data = gpx.tracks[0].segments[0].points
print(len(data))

# Start Position
start = data[0]
# End Position
finish = data[-1]

df = pd.DataFrame(columns=['lon', 'lat', 'alt', 'time'])
for point in data:
    df = df.append({'lon': point.longitude, 'lat': point.latitude, 'alt': point.elevation,
                    'time': matplotlib.dates.date2num(point.time)}, ignore_index=True)


# more options can be specified also
with pd.option_context('display.max_rows', 10, 'display.max_columns', None):
    print(df)

# fig = plt.plot(df['lon'], df['lat'])
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(df['time'], df['alt'])
fig.savefig('test.png')
