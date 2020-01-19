""" Parsing data from Komoot API """
import json

import grequests
from dateutil import parser
from slugify import slugify

START_DATE = parser.parse('2019-08-01')
END_DATE = parser.parse('2019-10-20')

print(START_DATE)
print(END_DATE)


def is_in_range(tour, start_date, end_date):
    """  Check if given date is in given range """
    return start_date <= parser.parse(tour['date'], ignoretz=True) <= end_date


def is_tour_completed(tour):
    """ Check if tour si completed """
    return tour["type"] == "tour_recorded"


def make_url(tour_id):
    """ Make GPX file url for Tour """
    return'https://external-api.komoot.de/v007/tours/' + str(tour_id) + '.gpx'


class FeedbackCounter:
    """Object to provide a feedback callback keeping track of total calls."""

    def __init__(self):
        self.counter = 0

    def feedback(self, r, **kwargs):
        self.counter += 1
        print("{0} fetched, {1} total.".format(r.url, self.counter))
        return r


def load_gpx_from_urls(urls):
    fbc = FeedbackCounter()
    requests = (grequests.get(u, callback=fbc.feedback) for u in urls)
    responses = grequests.map(requests)
    for response in responses:
        if 199 < response.status_code < 400:
            name = './data/' + slugify(response.url) + '.gpx'
            with open(name, 'wb') as f:
                f.write(response.content)
        else:
            print(response)


def main():
    """ Main """
    with open('./data/kom.json') as json_file:
        tours_data = json.load(json_file)['_embedded']['tours']
        filtered_tours_data = [tour for tour in tours_data if is_in_range(
            tour, START_DATE, END_DATE) and is_tour_completed(tour)]
        urls = [make_url(tour['id']) for tour in filtered_tours_data]
        print('Found tours for specified dates: ', len(filtered_tours_data))
        # print(*[t['name'] for t in filtered_tours_data], sep='\n')
        load_gpx_from_urls(urls)


main()
