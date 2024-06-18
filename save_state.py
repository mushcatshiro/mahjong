import pickle
import json


__all__ = ["State"]


class State:
    def save(self, pickled=True, json_format=False):
        if pickled:
            with open("save.pkl", "wb") as f:
                pickle.dump(self.__dict__.items(), f)
        if json_format:
            with open("save.json", "w") as f:
                json.dump(self.__dict__, f)

    def load(self, pickled=True, json_format=False):
        if pickled:
            with open("save.pkl", "rb") as f:
                for k, v in pickle.load(f):
                    setattr(self, k, v)
        if json_format:
            with open("save.json", "r") as f:
                for k, v in json.load(f).items():
                    setattr(self, k, v)
