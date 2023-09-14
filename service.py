import json
import requests
import abbreviation


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
    response = requests.get(url_2 + "groupId=" + group_name + "&startDate=" + start_date + "&endDate=" + end_date + "&removeEmptyDays")
    return json.loads(response.text)


if __name__ == "__main__":
    print(get_timetable_by_days("ВМ-ИВТ-2-1", "14.09.2023", "15.09.2023"))
    # res = getDay("18.09.2023", "ВМ-ИВТ-2-1")
    # for discipline in res["disciplines"]:
    #     print(f'Название: {discipline["name"]}')
    #     print(f'Время: {discipline["time"]}')
    #     print(f'Преподаватель: {discipline["teacherName"]}')
    #     print(f"Аудитория: {discipline['audienceId']}")
    #
    #     if discipline["subgroup"] == 0:
    #         pass
    #
    #     if discipline["type"] == "lec":
    #         print("Лекция")
    #     print("")
