import json
import requests
import abbreviation
from datetime import (datetime, timedelta)
from io import BytesIO


url = "http://merqury.fun:8080/api/timetable/groups"
response = requests.get(url)
groups = json.loads(response.text)


def getFaculties():
    res = []
    for group in groups:
        res.append(group["facultyName"])
    return res


def getGroupsByFaculty(facultyName: str):
    for group in groups:
        if abbreviation.abbreviation(group["facultyName"]) == facultyName:
            return list(group["groups"])
    return None


new_url = "http://merqury.fun:8080/api/timetable/day?"


def getDay(date, group_name):
    response = requests.get(new_url + "date=" + date + "&groupId=" + group_name)
    return json.loads(response.text)


def get_timetable_by_day(group_name, date):
    url_1 = "http://merqury.fun:8080/api/timetable/day?"
    response = requests.get(url_1 + "groupId=" + group_name + "&date=" + date)
    return json.loads(response.text)


def get_timetable_by_days(group_name, start_date, end_date):
    url_2 = "http://merqury.fun:8080/api/timetable/days?"
    response = requests.get(url_2 + "groupId=" + group_name + "&startDate=" + start_date +
                            "&endDate=" + end_date + "&removeEmptyDays")
    return json.loads(response.text)


def get_image_by_day(json):
    response = requests.post("http://merqury.fun:8080/api/timetable/image/day?vertical", json=json)
    return BytesIO(response.content).getvalue()


def get_image_by_6_days(json):
    response = requests.post("http://merqury.fun:8080/api/timetable/image/6days?horizontal", json=json)
    return BytesIO(response.content).getvalue()


class DateManager:
    @staticmethod
    def get_start_of_week(date: str):
        date1 = datetime.strptime(date, "%d.%m.%Y")
        day = date1.weekday()
        if day == 0:
            return date
        elif day == 1:
            return (date1 - timedelta(days=day)).strftime("%d.%m.%Y")
        elif day == 2:
            return (date1 - timedelta(days=day)).strftime("%d.%m.%Y")
        elif day == 3:
            return (date1 - timedelta(days=day)).strftime("%d.%m.%Y")
        elif day == 4:
            return (date1 - timedelta(days=day)).strftime("%d.%m.%Y")
        elif day == 5:
            return (date1 - timedelta(days=day)).strftime("%d.%m.%Y")
        elif day == 6:
            return (date1 - timedelta(days=day)).strftime("%d.%m.%Y")

    @staticmethod
    def get_end_of_week(date: str):
        date1 = datetime.strptime(date, "%d.%m.%Y")
        day = date1.weekday()
        if day == 0:
            return (date1 + timedelta(days=5)).strftime("%d.%m.%Y")
        elif day == 1:
            return (date1 + timedelta(days=4)).strftime("%d.%m.%Y")
        elif day == 2:
            return (date1 + timedelta(days=3)).strftime("%d.%m.%Y")
        elif day == 3:
            return (date1 + timedelta(days=2)).strftime("%d.%m.%Y")
        elif day == 4:
            return (date1 + timedelta(days=1)).strftime("%d.%m.%Y")
        elif day == 5:
            return date1.strftime("%d.%m.%Y")


if __name__ == "__main__":
    get_timetable_by_days("ВМ-ИВТ-2-1", "18.09.2023", "23.09.2023")
