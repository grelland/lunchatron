from datetime import date, datetime
from json import load
from urllib2 import urlopen, Request, URLError


def get_restaurants():
    try:
        return urlopen(Request("https://app.sio.no/api/middag/v1/open/content/restaurants", headers={
            "lang": "en"
        }))
    except URLError:
        return None


def list_restaurants():
    response = get_restaurants()
    if response:
        return load(response)
    else:
        return None


def find_restaurants(names):
    payload = list_restaurants()
    results = []

    if not payload:
        return results

    for restaurant in payload:
        # remove redundant spaces and convert string to lower
        # case in order to increase chances to find match
        restaurant_name = restaurant["name"].strip().lower()

        if restaurant_name in names and restaurant not in results:
            results.append(restaurant)

    return results


# returns true if restaurant is closed due to any events.
# For example: summer or winter breaks
def is_closed(schedule):
    today = date.today()

    for event in schedule:
        startdate = None
        enddate = None

        if event["startdate"]:
            startdate = datetime.strptime(event["startdate"], "%Y-%m-%d").date()

        if event["enddate"]:
            enddate = datetime.strptime(event["enddate"], "%Y-%m-%d").date()

        if (startdate and enddate) and (startdate <= today <= enddate):
            return True

        if (startdate and not enddate) and (today >= startdate):
            return True

        if (not startdate and enddate) and (today <= enddate):
            return True

    return False


def list_relevant_menu():
    restaurants = find_restaurants([
        "informatikkafeen"
    ])

    # dictionary where key is restaurant
    # name and value is menu
    results = {}

    # use current date as filter for menu
    today = date.today().strftime("%Y-%m-%d")

    for restaurant in restaurants:
        menu_week = restaurant["menu"]

        for menu in menu_week:
            menu_date = menu["date"]

            # do not add restaurant unless we are
            # sure that there is menu
            if menu_date == today:
                restaurant_menu = []

                for course in menu["dinner"]:
                    restaurant_menu.append(course["name"])

                results[restaurant["name"]] = restaurant_menu

                # put restaurant in only in
                # case when it is not closed
                # if not is_closed(restaurant["stengt"]):
                #    results[restaurant["name"]] = restaurant_menu

    return results


def prepare_message(restaurants):
    message = ""

    for restaurant in restaurants:
        message += restaurant + "\n\n"

        for course in restaurants[restaurant]:
            message += course + "\n"

    return {
        "text": message,
        "response_type": "in_channel"
    }


def run():
    restaurants = list_relevant_menu()
    print(prepare_message(restaurants))


run()
