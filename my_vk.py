import json

from vk_api import VkApi


class vk_class:
    def __init__(self):
        self.user = 0
        self.prop_data = {"login": "", "password": "", "multiplier": 1, "group": ""}
        self.multiplier = 1
        self.group_id = 0
        self.login = ""
        self.password = ""
        try:
            with open("res/properties.json", "r") as read_file_prop:
                self.prop_data = json.load(read_file_prop)
        except FileNotFoundError:
            with open("res/properties.json", "w") as write_file_prop:
                json.dump(self.prop_data, write_file_prop)
        self.set_properties()
        if self.login != "" and self.password != "":
            vk_session = VkApi(self.login, self.password)
            vk_session.auth()
            self.vk = vk_session.get_api()

    def set_properties(self):
        self.multiplier = self.prop_data["multiplier"]
        self.group_id = self.prop_data["group"]
        self.login = self.prop_data["login"]
        self.password = self.prop_data["password"]

    def auth(self):
        vk_session = VkApi(self.login, self.password)
        vk_session.auth()
        self.vk = vk_session.get_api()

    def get_posts(self, owner, count=50):
        try:
            get_wall = self.vk.wall.get(owner_id=int(owner), count=count)["items"]
        except ValueError:
            get_wall = self.vk.wall.get(domain=owner.split("/")[-1], count=count)["items"]
        all_posts = []
        for get_post in get_wall:
            data = {"post_id": get_post["id"], "owner_id": get_post["owner_id"], "ad": get_post["marked_as_ads"],
                    "likes": get_post["likes"]["count"], "views": get_post["views"]["count"],
                    "text": get_post["text"]}
            link = []
            data["img"] = link
            try:
                link = []
                for i in get_post["attachments"]:
                    link.append(i[i["type"]]["sizes"][-1]["url"])
                    if "attachments" in data:
                        try:
                            data["attachments"].append(
                                i["type"] + str(data["owner_id"]) + "_" + str(i[i["type"]]["id"]))
                        except KeyError:
                            pass
                    else:
                        try:
                            data["attachments"] = [i["type"] + str(data["owner_id"]) + "_" + str(i[i["type"]]["id"])]
                        except KeyError:
                            pass
                data["img"] = link
            except KeyError:
                pass
            all_posts.append(data)
        return all_posts

    def reload(self):
        try:
            with open("res/all_groups.json", "r") as read_file:
                data = json.load(read_file)
        except FileNotFoundError:
            return
        new_data = []
        likes = 0
        count = 0
        for i in data:
            for j in self.get_posts(i["id"]):
                if not j["ad"]:
                    likes += j["likes"]
                    count += 1
            new_data.append({"id": i["id"], "likes": likes // count})
        with open("res/all_groups.json", "w") as write_file:
            json.dump(new_data, write_file)
        return len(new_data)

    def append_group(self, groups_in):
        groups = groups_in.split()
        try:
            with open("res/all_groups.json", "r") as read_file:
                data = json.load(read_file)
        except FileNotFoundError:
            data = []
        for i in groups:
            req = self.get_posts(i)
            likes = 0
            count = 0
            for j in req:
                likes += j["likes"]
                count += 1
            data.append({"id": str(req[0]["owner_id"]), "likes": likes // count})
        yet = []
        for i in range(len(data) - 1, -1, -1):
            if data[i]["id"] in yet:
                del data[i]
            else:
                yet.append(data[i]["id"])
        with open("res/all_groups.json", "w") as write_file:
            json.dump(data, write_file)
        return len(data)

    def post(self, next_group=0):
        to_post = []
        try:
            with open("res/yet.txt", "r") as read_file:
                yet = read_file.read()
        except FileNotFoundError:
            yet = ""
        try:
            with open("res/all_groups.json", "r") as read_file:
                data = json.load(read_file)
        except FileNotFoundError:
            data = []
        if next_group == len(data):
            return ["end", "end", "end"]
        req = self.get_posts(data[next_group]["id"])
        for j in req:
            if j["likes"] > data[next_group]["likes"] * self.multiplier and j["ad"] == 0 and not (
                    str(j["post_id"]) in yet):
                yet += str(j["post_id"]) + " "
                to_post.append(
                    {"link": ('wall' + str(j['owner_id']) + '_' + str(j["post_id"])), "kf": j["likes"] / j["views"],
                     "info": "Лайки: " + str(j["likes"]) + "\nПросмотры: " + str(j["views"]), "text": j["text"],
                     "attachment": j["attachments"], "img": j["img"]})
        return [to_post, int(next_group / (len(data) - 1) * 100), next_group + 1]

    @staticmethod
    def remove_group(remove_in):
        try:
            with open("res/all_groups.json", "r") as read_file:
                data = json.load(read_file)
        except FileNotFoundError:
            data = []
        for i in remove_in.split():
            for j in range(len(data)):
                if data[j]["id"] == i:
                    del data[j]
                    break
        with open("res/all_groups.json", "w") as write_file:
            json.dump(data, write_file)
        return len(data)