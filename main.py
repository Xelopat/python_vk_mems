import json

from vk_api import VkApi

group_id = "-203614158"
login = '+79913396779'
password = 'Barsik262'
vk_session = VkApi(login, password)
vk_session.auth()
vk = vk_session.get_api()


def get_posts(owner, count=100):
    global vk
    try:
        get_wall = vk.wall.get(owner_id=int(owner), count=count)["items"]
    except ValueError:
        get_wall = vk.wall.get(domain=owner.split("/")[-1], count=count)["items"]
    all_posts = []
    for post in get_wall:
        data = {"post_id": post["id"], "owner_id": post["owner_id"], "ad": post["marked_as_ads"],
                "likes": post["likes"]["count"], "views": post["views"]["count"]}
        try:
            for i in post["attachments"]:
                if "attachments" in data:
                    try:
                        data["attachments"].append(i["type"] + str(data["owner_id"]) + "_" + str(i[i["type"]]["id"]))
                    except KeyError:
                        print("Error type")
                else:
                    try:
                        data["attachments"] = [i["type"] + str(data["owner_id"]) + "_" + str(i[i["type"]]["id"])]
                    except KeyError:
                        print("Error type")
        except KeyError:
            print("Error attachment")
        all_posts.append(data)
    return all_posts


def reload():
    try:
        with open("all_groups.json", "r") as read_file:
            data = json.load(read_file)
    except FileNotFoundError:
        print("None")
        return
    new_data = []
    likes = 0
    count = 0
    for i in data:
        for j in get_posts(i["group"]):
            if not j["ad"]:
                likes += j["likes"]
                count += 1
        new_data.append({i["group"]: likes // count})
    with open("all_groups.json", "w") as write_file:
        json.dump(new_data, write_file)


def append_group(groups_in):
    groups = groups_in.split()
    try:
        with open("all_groups.json", "r") as read_file:
            data = json.load(read_file)
    except FileNotFoundError:
        data = []
    for i in groups:
        req = get_posts(i)
        likes = 0
        count = 0
        for j in req:
            likes += j["likes"]
            count += 1
        data.append({str(req[0]["owner_id"]): likes // count})
    yet = []
    for i in range(len(data) - 1, -1, -1):
        if data[i].keys() in yet:
            del data[i]
        else:
            yet.append(data[i].keys())
    with open("all_groups.json", "w") as write_file:
        json.dump(data, write_file)


def remove_group(remove_in):
    try:
        with open("all_groups.json", "r") as read_file:
            data = json.load(read_file)
    except FileNotFoundError:
        data = []
    for i in remove_in.split():
        for j in range(len(data)):
            if [x for x in data[j].keys()][0] == i:
                del data[j]
                break
    with open("all_groups.json", "w") as write_file:
        json.dump(data, write_file)

remove_group(input())
