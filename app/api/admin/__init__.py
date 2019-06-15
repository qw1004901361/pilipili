# coding=UTF-8
from flask import Blueprint

from app.api.admin import auth, base, comment, log, video, animation, role, tag, user, admin, bangumi


def create_admin_blueprint():
    admin_blueprint = Blueprint("admin", __name__, url_prefix="/api/admin")
    admin.admin.register(admin_blueprint, url_prefix="/admin")
    animation.animation.register(admin_blueprint, url_prefix="/animation")
    auth.auth.register(admin_blueprint, url_prefix="/auth")
    bangumi.bangumi.register(admin_blueprint, url_prefix="/bangumi")
    base.base.register(admin_blueprint, url_prefix="")
    comment.comment.register(admin_blueprint, url_prefix="/comment")
    log.log.register(admin_blueprint, url_prefix="/log")
    role.role.register(admin_blueprint, url_prefix="/role")
    tag.tag.register(admin_blueprint, url_prefix="/tag")
    user.user.register(admin_blueprint, url_prefix="/user")
    video.video.register(admin_blueprint, url_prefix="/video")
    return admin_blueprint
