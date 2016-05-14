import csv
import requests
from bs4 import BeautifulSoup

def to_utf8(val):
    return val.encode('utf-8')

def to_int_or_none(val):
    try:
        return int(val)
    except ValueError:
        return None

DATA_MAP = (
    # (field_name, soup_kwargs, attribute, parser)
    ('name', {'class_': 'cTitle'}, 'title', to_utf8),
    ('industry', {'class_': 'cInd'}, 'title', to_utf8),
    # we have to use data attributes here instead of classes, because there's a
    # mistake in fairy godboss's HTML in which unpaid paternity has the same
    # class as unpaid maternity.
    ('maternity_leave', {'attrs': {'data-paid-maternity': True}}, 'data-paid-maternity', to_int_or_none),
    ('unpaid_maternity_leave', {'attrs': {'data-unpaid-maternity': True}}, 'data-unpaid-maternity', to_int_or_none),
    ('paternity_leave', {'attrs': {'data-paid-paternity': True}}, 'data-paid-paternity', to_int_or_none),
    ('unpaid_paternity_leave', {'attrs': {'data-unpaid-paternity': True}}, 'data-unpaid-paternity', to_int_or_none),
)

CSV_FILE = 'data.csv'

def main():
    dataset = []
    host = 'https://fairygodboss.com'
    url = '/maternity-leave-resource-center'


    with open(CSV_FILE, 'wb') as csvfile:
        csvwriter = csv.writer(csvfile)

        # Write a heading row to the CSV:
        csvwriter.writerow([x[0] for x in DATA_MAP])

        while url is not None:
            request = requests.get(host + url)
            soup = BeautifulSoup(request.text, "lxml")
            items = soup.find_all(id='list', limit=1)[0].find_all('li')

            print "Downloading page at {}{}".format(host, url)

            # Parse each row
            for item in items:
                row = []
                # Parse each cell
                for field in DATA_MAP:
                    parser = field[3]
                    parsed_item = parser(item.find_all(limit=1, **field[1])[0].attrs[field[2]])
                    row.append(parsed_item)
                # Write the row to the CSV:
                csvwriter.writerow(row)

            # Extract the next page url and start the loop again
            try:
                next_button = soup.find_all(rel='next')[0]
                url = next_button.attrs['href']
            except IndexError:
                url = None

if __name__ == '__main__':
    main()
