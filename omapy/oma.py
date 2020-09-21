
__author__ = "Martin Aigner"

import requests
import json
import numpy as np

class Login:
    def __init__(self, endpoint, access_token, verify_certificate=True):
        self.endpoint = endpoint
        self.access_token = access_token
        self.verify_certificate = verify_certificate
        self.headers = {
            'User-Agent': 'oma.py',
            'Authorization': "Bearer " + access_token
        }
        self.config = {
            "api_path": "api/",
            "cache_dir": "omacache"
        }

    def recording(self, id):
        r = Recording(id, self)
        r.get()
        return r

    def composer(self, id):
        c = Composer(id, self)
        c.get()
        return c

    def annotation_session(self, id):
        s = AnnotationSession(id, self)
        s.get()
        return s


class ApiObject:
    def __init__(self):
        self.__data_cache = None
        self.oma_login = None
        self.params = {}

    def get(self):
        self.params[self.objectName] = self.id
        url = self.oma_login.endpoint + self.oma_login.config["api_path"] + self.objectName
        response = requests.post(url, headers=self.oma_login.headers, data=self.params, verify=self.oma_login.verify_certificate)
        try:
            content = json.loads(response.content.decode())
        except:
            content = {"error": response}
        self.__data_cache = content

    def dictionary(self):
        if self.__data_cache is None:
            self.get()
        return self.__data_cache


class AnnotationSession(ApiObject):
    def __init__(self, id, oma_login):
        self.id = id
        self.objectName = "session"
        self.oma_login = oma_login
        self.params = {"method": "get"}

    def get_tempo_chart(self):
        annotations = self.dictionary()["annotations"]
        index = 0
        bar_numbers = np.zeros(len(annotations), dtype=int)
        bar_tempos = np.zeros(len(annotations))

        for current_annotation in range(len(annotations) - 1):
            annotation = annotations[current_annotation]
            # only take whole bars for now
            if annotation["beatNumber"] != 1:
                continue

            bar_numbers[index] = annotation["barNumber"]
            current_bar_start = annotation["momentOfPerception"]
            next_bar_start = annotations[current_annotation + 1]["momentOfPerception"]
            duration = next_bar_start - current_bar_start

            if duration > 0:
                bar_tempos[index] = 1 / duration # or some other metric
            else:
                bar_tempos[index] = None
            index = index + 1

        return (bar_numbers[0:index], bar_tempos[0:index])



class Recording(ApiObject):
    def __init__(self, id, oma_login):
        self.id = id
        self.objectName = "recording"
        self.oma_login = oma_login
        self.params = {"method": "get"}

    def get_annotation_sessions(self):
        sessions = ApiObject()
        sessions.params["method"] = "findBy"
        sessions.params["findBy"] = "recording"
        sessions.params["recording"] = self.id
        sessions.objectName = "annotation"
        sessions.id = 0
        sessions.oma_login = self.oma_login
        sessions.get()

        return sessions.dictionary()



class Composer(ApiObject):
    def __init__(self, id, oma_login):
        self.id = id
        self.objectName = "composer"
        self.oma_login = oma_login
        self.params = {"method": "get"}

