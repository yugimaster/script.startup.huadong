# -*- coding: utf8 -*-

import xbmc
import xbmcaddon
import xbmcgui
from OnClickHandler import OnClickHandler
from dialogs.DialogBaseInfo import DialogBaseInfo
from BaseClasses import *
from common import *
from pinyin import PinYinAPI

ch = OnClickHandler()
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_DATA_PATH = xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID).decode("utf-8")
MOVIE_DATA_PATH = "D:/"
C_LIST_ACTORS = 3001
C_LIST_RECOMMEMD = 6000
C_BUTTON_PLAY = 201


class WindowMovieDetail(WindowXML, DialogBaseInfo):

    def __init__(self, *args, **kwargs):
        super(WindowMovieDetail, self).__init__(*args, **kwargs)
        self.title = kwargs.get("title")
        self.vid = kwargs.get("video_id")
        self.type = kwargs.get("resource_type")
        self.path = kwargs.get("path")
        self.file_path = ""

    def onInit(self):
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        if self.type == "local":
            self.parse_local_movie_info(self.path)
        elif self.type == "cloud":
            self.getControl(C_BUTTON_PLAY).setLabel(u"下  载")
            name_pinyin = PinYinAPI.getPinYinFirstLetter(self.title.decode('utf-8'))
            self.parse_cloud_movie_info(name_pinyin)

    def onAction(self, action):
        super(WindowMovieDetail, self).onAction(action)
        ch.serve_action(action, self.getFocusId(), self)

    def onClick(self, control_id):
        super(WindowMovieDetail, self).onClick(control_id)
        ch.serve(control_id, self)

    @ch.click(C_BUTTON_PLAY)
    def video_action(self):
        if self.type == "local":
            listitem = xbmcgui.ListItem(self.title)
            xbmc.Player().play(self.file_path, listitem)
            xbmc.executebuiltin("ActivateWindow(fullscreenvideo)")
        elif self.type == "cloud":
            pass

    def parse_local_movie_info(self, path):
        data = self.get_local_movie_detail_json(path)
        poster_path = data["movie"]["poster"]
        score = data["movie"]["score"]
        directors = data["movie"]["director"]
        actors = data["movie"]["actors"]
        self.file_path = path + data["movie"]["url"]
        stars = self.get_stars_from_score(str(int(score) * 2))
        self.parse_local_recommend_list()
        self.window.setProperty("PosterImage", path + poster_path)
        self.window.setProperty("MovieStars", stars)
        self.window.setProperty("MovieTitle", self.title)
        self.window.setProperty("MovieDirector", directors.replace(",", u"、"))
        actors = actors.split(",")
        if actors:
            self.set_actor_list(actors)
        self.window.setProperty("MoviePlot", data["movie"]["description"])

    def parse_cloud_movie_info(self, name):
        data = self.get_cloud_movie_detail_json(name)
        poster_path = ADDON_PATH + data["v"]["fanart"]
        recommend_list = data["recommend"]
        mark = data["v"]["mark"]
        stars = self.get_stars_from_score(mark)
        self.parse_cloud_recommend_list(recommend_list[:6])
        self.window.setProperty("PosterImage", poster_path)
        self.window.setProperty("MovieStars", stars)
        self.window.setProperty("MovieTitle", self.title)
        self.window.setProperty("MovieDirector", data["v"]["director"])
        actors = data["v"]["actors"]
        if actors:
            self.set_actor_list(actors)
        self.window.setProperty("MoviePlot", data["v"]["content"])

    @run_async
    def parse_local_recommend_list(self):
        data = self.get_local_movie_relate_json(self.path)
        listitems = []
        for item in data["relateList"]:
            liz = {"label": item["name"],
                   "icon": MOVIE_DATA_PATH + item["imgUrl"],
                   "path": MOVIE_DATA_PATH + item["url"],
                   "type": "local"}
            listitems.append(liz)
        self.set_container(C_LIST_RECOMMEMD, listitems)

    @run_async
    def parse_cloud_recommend_list(self, lists):
        listitems = []
        for item in lists:
            liz = {"label": item["title"],
                   "vid": item["id"],
                   "icon": "http://img24.pplive.cn/sp423/" + item["extraData"]["coverPic"]}
            listitems.append(liz)
        self.set_container(C_LIST_RECOMMEMD, listitems)

    def set_actor_list(self, lists):
        listitems = []
        if self.type == "local":
            for (count, item) in enumerate(lists):
                if count == len(lists) - 1:
                    liz = {"label": item}
                else:
                    liz = {"label": item + u"、"}
                listitems.append(liz)
        elif self.type == "cloud":
            for (count, item) in enumerate(lists):
                if item["name"] == "null":
                    continue
                if count == len(lists) - 1:
                    liz = {"label": item["name"]}
                else:
                    liz = {"label": item["name"] + u"、"}
                listitems.append(liz)
        self.set_container(C_LIST_ACTORS, listitems)

    def get_stars_from_score(self, score):
        if not score:
            return "0"
        f_score = float(score) / 2.0
        if f_score < 0.3:
            stars = "0"
        elif f_score < 0.8:
            stars = "0.5"
        elif f_score < 1.3:
            stars = "1"
        elif f_score < 1.8:
            stars = "1.5"
        elif f_score < 2.3:
            stars = "2"
        elif f_score < 2.8:
            stars = "2.5"
        elif f_score < 3.3:
            stars = "3"
        elif f_score < 3.8:
            stars = "3.5"
        elif f_score < 4.3:
            stars = "4"
        elif f_score < 4.8:
            stars = "4.5"
        else:
            stars = "5"
        return stars

    def get_local_movie_detail_json(self, path):
        return get_json_file(path + "desc.json")

    def get_local_movie_relate_json(self, path):
        return get_json_file(path + "relatelist.json")

    def get_cloud_movie_detail_json(self, name):
        return get_json_file(ADDON_PATH + "/data/" + name + "/desc.json")
