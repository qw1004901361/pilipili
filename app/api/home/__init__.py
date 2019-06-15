# coding=UTF-8
from flask import Blueprint

from app.api.home import base, comment, personal, bangumi, search, video


def create_home_blueprint():
    home = Blueprint("home", __name__, url_prefix="/api")
    base.base.register(home, url_prefix="")
    video.video.register(home, url_prefix="/video")
    comment.comment.register(home, url_prefix="/comment")
    personal.personal.register(home, url_prefix="/personal")
    bangumi.bangumi.register(home, url_prefix="/bangumi")
    search.search.register(home, url_prefix="/search")
    return home
