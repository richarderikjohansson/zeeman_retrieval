from datetime import datetime, timedelta
import requests


def get_temperature(dt):
    """
    Function that gets the temperature from IRF's weather database

    Parameters:
    dt (datetime): datetime object from when measurement started

    Returns:
    (float): Temperature at IRF in Kelvin at date and time "dt"
    """
    # need to switch day if measurement started at 00:xx:xx
    shift_flag = dt.hour == 0

    # make target, get data from database and make a dictionary from data
    target = make_target(dt, shift_flag)
    response = perform_request(target)
    dictionary = clean_content(response)

    # shift dt to match content from response
    new_dt = dt - timedelta(hours=1)
    min_key = min(dictionary.keys(), key=lambda k: abs(k - new_dt))
    return dictionary[min_key]


def clean_content(response):
    """
    Function to organize the response content from IRF's weather database

    Parameters:
    response (Response): response object created from the GET request to the database

    Returns:
    dictionary (dict): dictionary containing datetime objects as keys and temperature in
    Celsius as values

    """
    content = response.content.decode("utf-8").split("\n")
    dictionary = {}

    # make checks that fields contain the data needed
    for element in content:
        sub = element.split()
        if len(sub) > 1 and sub[0] != "x" and sub[1] != "x":
            dt = datetime.strptime(sub[0], "%Y%m%d%H%M%S")
            dictionary[dt] = float(sub[1])

    return dictionary


def make_target(datetime_object, shift_day):
    """
    Function that creates the target for the GET request to the database

    Parameters:
    date_timeobject (datetime): datetime object for the day that the temperature data should contain

    Returns:
    target (str): url string that is being put intro the GET request

    """
    # edge case if measurement started on a new day -> shift to previous to match dates in database
    if shift_day:
        new_dt = datetime_object - timedelta(hours=1)
        year = new_dt.year
        month = new_dt.month
        day = new_dt.day
    else:
        year = datetime_object.year
        month = datetime_object.month
        day = datetime_object.day

    target = f"https://www2.irf.se/weather/get_day_ascii.php?year={year}&month={month}&day={day}"
    return target


def perform_request(target):
    """
    performs GET request to the weather database
    and returns the response object

    Parameters:
    target (str): url string that is being put intro the GET request
    """
    # check that the response is ok
    r = requests.get(target, timeout=10)
    if r.status_code != 200:
        print(r, "can not connect to dc")
    else:
        response = requests.get(url=target, timeout=10)
        return response
    return None
