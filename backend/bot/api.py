import os
from ossapi import Ossapi

osu_api = Ossapi(os.environ.get("CLIENT_ID"), os.environ.get("CLIENT_SECRET"))
