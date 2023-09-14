import service


def abbreviation(s: str):
    if s == "Аспирантура":
        return s

    result = ""
    modified_stroke = s.replace(",", "").replace("-", " ")
    sntns = modified_stroke.split("(")

    if "исторический факультет".lower() in modified_stroke.lower():
        result = "ИстФак"
    else:
        words = sntns[0].split(" ")
        for word in words:
            if word == "":
                continue
            if len(word) == 1:
                result += word.lower()
            else:
                result += word.upper()[0]

    if "(" in s:
        result += " ("

    for i in range(1, len(sntns)):
        result += sntns[i]

    return result


if __name__ == '__main__':

    for faculty in service.getFaculties():
        print(abbreviation(faculty))
