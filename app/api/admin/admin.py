# coding=UTF-8
from flasgger import swag_from
from flask import current_app
from flask_login import login_required
from sqlalchemy import or_

from app.forms.other import PageForm, IdForm, SearchForm
from app.forms.user import AdminAddForm, SuperAdminEditForm
from app.libs.auth import user_auth
from app.libs.enums import ReturnEnum
from app.libs.redprint import Redprint
from app.libs.utils import write_oplog
from app.models.base import db
from app.models.user import User, BaseUser, Admin, UserRole, Role
from app.view_models.return_obj import ReturnObj

"""
管理管理员模块（超级管理员）
添加管理员
列出管理员
删除管理员
编辑管理员
"""

admin = Redprint("admin")


@admin.route("/list")
@login_required
# @user_auth
@swag_from("../../yml/admin/admin/list_admin.yml")
def list_admin():
    """分页列出管理员的信息"""
    form = PageForm().validate_for_api()
    page_data = BaseUser.query.join(Admin, Admin.id == BaseUser.id)
    # 判断是否搜索
    if form.q.data:
        page_data = page_data.filter(or_(BaseUser.id == form.q.data, BaseUser.name == "%" + form.q.data + "%"))
    page_data = page_data.paginate(error_out=False, page=int(form.page.data), per_page=int(form.pagesize.data))
    admins = []
    for i in page_data.items:
        roles = []
        for j in Role.query.join(UserRole, UserRole.role_id == Role.id).filter(UserRole.user_id == i.id).all():
            role = {
                "id": j.id,
                "name": j.name
            }
            roles.append(role)
        admin = {
            "id": i.id,
            "account": i.account,
            "name": i.name,
            "gender": i.gender,
            "roles": roles
        }
        admins.append(admin)
    r = {
        "has_next": page_data.has_next,
        "has_prev": page_data.has_prev,
        "pages": page_data.pages,
        "page": page_data.page,
        "total": page_data.total,
        "admins": admins
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@admin.route("/view")
@login_required
# @user_auth
@swag_from("../../yml/admin/admin/view_admin.yml")
def view_admin():
    """查找管理员，根据id或者名字查找"""
    form = SearchForm().validate_for_api()
    q = form.q.data
    page_data = BaseUser.query.join(Admin, BaseUser.id == Admin.id). \
        filter(or_(BaseUser.name.like("%" + q + "%"), BaseUser.id == q.lower().replace("uid", ""))). \
        paginate(error_out=False, page=int(form.page.data), per_page=int(current_app.config["ADMIN_PER_USER_PAGE"]))
    admins = []
    for i in page_data.items:
        roles = []
        for j in Role.query.join(UserRole, UserRole.role_id == Role.id).filter(UserRole.user_id == i.id).all():
            role = {
                "id": j.id,
                "name": j.name
            }
            roles.append(role)
        admin = {
            "id": i.id,
            "account": i.account,
            "name": i.name,
            "gender": i.gender,
            "roles": roles
        }
        admins.append(admin)
    r = {
        "has_next": page_data.has_next,  # 是否有下一页 bool
        "has_prev": page_data.has_prev,  # 是否有上一页 bool
        "pages": page_data.pages,  # 总共的页数
        "page": page_data.page,  # 当前页数
        "total": page_data.total,  # 总共的数据
        "admins": admins  # 数据
    }
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data=r)


@admin.route("/add", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/admin/add_admin.yml", methods=['POST'])
def add_admin():
    """添加管理员"""
    form = AdminAddForm()
    # 动态加载最新的角色列表
    form.role_id.choices = [(v.id, v.id) for v in Role.query.all()]
    # 验证
    form.validate_for_api()
    baseuser = register_admin(form)
    if baseuser:
        write_oplog()
        return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data={"id": baseuser.id})
    return ReturnObj.get_response(ReturnEnum.FAIL.value, "fail")


@admin.route("/del")
@login_required
# @user_auth
@swag_from("../../yml/admin/admin/del_admin.yml")
def del_admin():
    """删除管理员"""
    form = IdForm().validate_for_api()
    baseuser = BaseUser.query.join(Admin, Admin.id == BaseUser.id).filter(Admin.id == form.id.data). \
        first_or_404(description="找不到该用户")
    with db.auto_commit():
        # 删除管理员关联的角色
        for user_role in UserRole.query.filter(UserRole.user_id == baseuser.id).all():
            db.session.delete(user_role)
        # 删除管理员额外信息
        admin = Admin.query.filter(Admin.id == baseuser.id).first()
        if admin:
            db.session.delete(admin)
            # 如果管理员还有用户的角色，删除
            user = User.query.filter(User.id == baseuser.id).first()
            if user:
                db.session.delete(user)
        # 删除基本信息
        db.session.delete(baseuser)
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success")


@admin.route("/edit", methods=["POST"])
@login_required
# @user_auth
@swag_from("../../yml/admin/admin/edit_admin.yml", methods=['POST'])
def edit_admin():
    """编辑管理员"""
    form = SuperAdminEditForm()
    # 动态加载最新的角色列表
    form.role_id.choices = [(v.id, v.id) for v in Role.query.all()]
    # 验证
    form.validate_for_api()
    baseuser = form.obj
    # 数据库操作
    try:
        # 更新基本用户信息
        if form.pwd.data:
            baseuser.pwd = form.pwd.data
        if form.gender.data:
            baseuser.gender = form.gender.data
        if form.name.data:
            baseuser.name = form.name.data
        db.session.add(baseuser)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    with db.auto_commit():
        if form.role_id.data:
            # 删除原来的角色信息
            user_roles = UserRole.query.filter(UserRole.user_id == baseuser.id).all()
            for i in user_roles:
                db.session.delete(i)
            # 添加新的角色
            for i in form.role_id.data:
                db.session.add(UserRole(user_id=baseuser.id, role_id=i))
    write_oplog()
    return ReturnObj.get_response(ReturnEnum.SUCCESS.value, "success", data={"id": baseuser.id})


def register_admin(form):
    """添加管理员，写入数据库"""
    try:
        # 基本用户
        baseuser = BaseUser()
        baseuser.account = form.account.data
        baseuser.pwd = form.pwd.data
        baseuser.name = form.name.data
        baseuser.gender = form.gender.data
        db.session.add(baseuser)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_BASEUSER_FAIL.value, "添加用户基本信息失败")
    baseuser = BaseUser.query.filter(BaseUser.account == form.account.data).first()
    try:
        # 用户其他信息
        admin = Admin()
        admin.id = baseuser.id
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_ADMIN_FAIL.value, "添加用户管理员信息失败")
    try:
        # 赋予用户相应角色
        for i in form.role_id.data:
            user_role = UserRole()
            user_role.user_id = baseuser.id
            user_role.role_id = i
            db.session.add(user_role)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
        return ReturnObj.get_response(ReturnEnum.ADD_USERROLE_FAIL.value, "赋予用户角色失败")
    return baseuser
