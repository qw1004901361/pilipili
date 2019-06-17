# coding=UTF-8
import random
import uuid
import datetime

from sqlalchemy.orm import sessionmaker

from app.libs.enums import GenderEnum
from app.libs.utils import id_generator
from app.models.video import Video, Tag, Comment, VideoCol, Animation, Bangumi, BangumiCol
from app.models.user import Admin, BaseUser, User, AuthModule, AuthApi, Role, RoleAuth, UserRole, Follow

from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://qw:qw@971230@134.175.93.183:3306/pilipili")

Session = sessionmaker(bind=engine)


def init():
    pass
    # # 删除用户
    # for i in session.query(User).all():
    #     session.delete(i)
    # for i in session.query(Admin).all():
    #     session.delete(i)
    # for i in session.query(BaseUser).all():
    #     session.delete(i)
    # session.commit()
    #
    # # 删除角色
    # for i in session.query(Role).all():
    #     session.delete(i)
    # for i in session.query(UserRole).all():
    #     session.delete(i)
    # session.commit()
    #
    # # 删除权限
    # for i in session.query(AuthApi).all():
    #     session.delete(i)
    # for i in session.query(AuthModule).all():
    #     session.delete(i)
    # for i in session.query(RoleAuth).all():
    #     session.delete(i)
    # session.commit()
    #
    # # 删除评论
    # for i in session.query(Tag).all():
    #     session.delete(i)
    # for i in session.query(Comment).all():
    #     session.delete(i)
    # # 删除收藏
    # for i in session.query(VideoCol).all():
    #     session.delete(i)
    # # 删除视频
    # for i in session.query(Video).all():
    #     session.delete(i)
    # # 删除预告
    # for i in session.query(Animation).all():
    #     session.delete(i)
    # session.commit()
    #
    # # 删除日志
    # for i in session.query(UserLog).all():
    #     session.delete(i)
    # for i in session.query(AdminLog).all():
    #     session.delete(i)
    # for i in session.query(Oplog).all():
    #     session.delete(i)
    # session.commit()


def generate():
    session = Session()

    """生成权限模块"""
    # 管理员模块
    auth_module1 = AuthModule(name="管理员模块", module="admin.admin")
    session.add(auth_module1)
    session.commit()
    # admin_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module1.id,
    #                      name="添加管理员", api="add_admin")
    # admin_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module1.id,
    #                      name="删除管理员", api="del_admin")
    # admin_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module1.id,
    #                      name="列出管理员", api="list_admin")
    # admin_api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module1.id,
    #                      name="查找管理员", api="view_admin")
    # admin_api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module1.id,
    #                      name="编辑管理员", api="edit_admin")
    # session.add(admin_api1)
    # session.add(admin_api2)
    # session.add(admin_api3)
    # session.add(admin_api4)
    # session.add(admin_api5)
    # session.commit()

    # 评论模块
    auth_module2 = AuthModule(name="评论模块", module="admin.comment")
    session.add(auth_module2)
    session.commit()
    # comment_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module2.id,
    #                        name="删除评论", api="del_comment")
    # comment_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module2.id,
    #                        name="列出评论", api="list_comment")
    # comment_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module2.id,
    #                        name="查找评论", api="view_comment")
    # session.add(comment_api1)
    # session.add(comment_api2)
    # session.add(comment_api3)
    # session.commit()

    # 日志模块
    auth_module3 = AuthModule(id=str(uuid.uuid1()), name="日志模块", module="admin.log")
    session.add(auth_module3)
    session.commit()
    # log_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module3.id,
    #                    name="列出操作日志", api="list_oplog")
    # log_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module3.id,
    #                    name="列出管理员登录日志", api="list_adminloginlog")
    # log_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module3.id,
    #                    name="列出用户登录日志", api="list_userloginlog")
    # session.add(log_api1)
    # session.add(log_api2)
    # session.add(log_api3)
    # session.commit()

    # 视频模块
    auth_module4 = AuthModule(id=str(uuid.uuid1()), name="视频模块",
                              module="admin.video")
    session.add(auth_module4)
    session.commit()
    # api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module4.id,
    #                name="添加视频", api="add_movie")
    # api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module4.id,
    #                name="删除视频", api="list_movie")
    # api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module4.id,
    #                name="列出视频", api="edit_movie")
    # api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module4.id,
    #                name="查找视频", api="del_movie")
    # api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module4.id,
    #                name="编辑视频", api="view_movie")
    # session.add(api1)
    # session.add(api2)
    # session.add(api3)
    # session.add(api4)
    # session.add(api5)
    # session.commit()

    # 轮播图模块
    auth_module6 = AuthModule(id=str(uuid.uuid1()), name="视频预告模块",
                              module="admin.animation")
    session.add(auth_module6)
    session.commit()
    # preview_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module6.id,
    #                        name="添加视频预告", api="add_preview")
    # preview_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module6.id,
    #                        name="删除视频预告", api="list_preview")
    # preview_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module6.id,
    #                        name="列出视频预告", api="edit_preview")
    # preview_api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module6.id,
    #                        name="查找视频预告", api="del_preview")
    # preview_api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module6.id,
    #                        name="编辑视频预告", api="view_preview")
    # session.add(preview_api1)
    # session.add(preview_api2)
    # session.add(preview_api3)
    # session.add(preview_api4)
    # session.add(preview_api5)
    # session.commit()

    # 角色模块
    auth_module7 = AuthModule(name="角色模块", module="admin.role")
    session.add(auth_module7)
    session.commit()
    role_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module7.id,
                        name="添加角色", api="add_role")
    role_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module7.id,
                        name="删除角色", api="list_role")
    role_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module7.id,
                        name="列出角色", api="edit_role")
    role_api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module7.id,
                        name="查找角色", api="del_role")
    role_api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module7.id,
                        name="编辑角色", api="view_role")
    session.add(role_api1)
    session.add(role_api2)
    session.add(role_api3)
    session.add(role_api4)
    session.add(role_api5)
    session.commit()

    # 标签模块
    auth_module8 = AuthModule(id=str(uuid.uuid1()), name="标签模块",
                              module="admin.tag")
    session.add(auth_module8)
    session.commit()
    tag_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module8.id,
                       name="添加标签", api="add_tag")
    tag_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module8.id,
                       name="删除标签", api="list_tag")
    tag_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module8.id,
                       name="列出标签", api="edit_tag")
    tag_api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module8.id,
                       name="查找标签", api="del_tag")
    tag_api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module8.id,
                       name="编辑标签", api="view_tag")
    session.add(tag_api1)
    session.add(tag_api2)
    session.add(tag_api3)
    session.add(tag_api4)
    session.add(tag_api5)
    session.commit()

    # 普通用户模块
    auth_module9 = AuthModule(id=str(uuid.uuid1()), name="普通用户模块",
                              module="admin.user")
    session.add(auth_module9)
    session.commit()
    user_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module9.id,
                        name="添加用户", api="add_user")
    user_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module9.id,
                        name="删除用户", api="list_user")
    user_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module9.id,
                        name="列出用户", api="edit_user")
    user_api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module9.id,
                        name="查找用户", api="del_user")
    user_api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module9.id,
                        name="编辑用户", api="view_user")
    session.add(user_api1)
    session.add(user_api2)
    session.add(user_api3)
    session.add(user_api4)
    session.add(user_api5)
    session.commit()

    # 权限模块
    auth_module10 = AuthModule(id=str(uuid.uuid1()), name="权限模块",
                               module="admin.auth")
    session.add(auth_module10)
    session.commit()
    auth_api1 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="添加权限模块", api="add_auth_module")
    auth_api2 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="删除权限模块", api="list_auth_module")
    auth_api3 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="列出权限模块", api="edit_auth_module")
    auth_api4 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="查找权限模块", api="del_auth_module")
    auth_api5 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="编辑权限模块", api="view_auth_module")
    auth_api6 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="添加权限接口", api="add_auth_api")
    auth_api7 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="删除权限接口", api="list_auth_api")
    auth_api8 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="列出权限接口", api="edit_auth_api")
    auth_api9 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                        name="查找权限接口", api="del_auth_api")
    auth_api10 = AuthApi(id=str(uuid.uuid1()), module_id=auth_module10.id,
                         name="编辑权限接口", api="view_auth_api")

    session.add(auth_api1)
    session.add(auth_api2)
    session.add(auth_api3)
    session.add(auth_api4)
    session.add(auth_api5)
    session.add(auth_api6)
    session.add(auth_api7)
    session.add(auth_api8)
    session.add(auth_api9)
    session.add(auth_api10)
    session.commit()

    """角色权限关联"""
    # 普通用户
    session.add(RoleAuth(role_id=role1.role_id, auth_id="1"))

    # 用户管理员：普通用户模块
    session.add(RoleAuth(role_id=role2.role_id, auth_id=auth_module9.id))

    # 视频管理员：评论模块，视频模块，视频收藏模块，视频预告模块，标签模块
    session.add(RoleAuth(role_id=role3.role_id, auth_id=auth_module2.id))
    session.add(RoleAuth(role_id=role3.role_id, auth_id=auth_module4.id))
    session.add(RoleAuth(role_id=role3.role_id, auth_id=auth_module5.id))
    session.add(RoleAuth(role_id=role3.role_id, auth_id=auth_module6.id))
    session.add(RoleAuth(role_id=role3.role_id, auth_id=auth_module8.id))

    # 日志管理员：日志模块
    session.add(RoleAuth(role_id=role4.role_id, auth_id=auth_module3.id))

    # 超级管理员：所有模块
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module1.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module2.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module3.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module4.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module5.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module6.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module7.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module8.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module9.id))
    session.add(RoleAuth(role_id=role5.role_id, auth_id=auth_module10.id))
    session.commit()


def generate_auth_module():
    """生成权限模块"""
    session = Session()
    try:
        auth_module1 = AuthModule(id=1, name="管理员模块", module="admin.admin")
        auth_module2 = AuthModule(id=2, name="轮播图模块", module="admin.animation")
        auth_module3 = AuthModule(id=3, name="权限模块", module="admin.auth")
        auth_module4 = AuthModule(id=4, name="番剧模块", module="admin.bangumi")
        auth_module5 = AuthModule(id=5, name="评论模块", module="admin.comment")
        auth_module6 = AuthModule(id=6, name="日志模块", module="admin.log")
        auth_module7 = AuthModule(id=7, name="角色模块", module="admin.role")
        auth_module8 = AuthModule(id=8, name="标签模块", module="admin.tag")
        auth_module9 = AuthModule(id=9, name="用户模块", module="admin.user")
        auth_module10 = AuthModule(id=10, name="视频模块", module="admin.video")
        session.add(auth_module1)
        session.add(auth_module2)
        session.add(auth_module3)
        session.add(auth_module4)
        session.add(auth_module5)
        session.add(auth_module6)
        session.add(auth_module7)
        session.add(auth_module8)
        session.add(auth_module9)
        session.add(auth_module10)
        session.commit()
    except Exception as e:
        session.rollback()

    role2 = session.query(Role).filter(Role.name == "用户管理员").first()
    role3 = session.query(Role).filter(Role.name == "视频管理员").first()
    role4 = session.query(Role).filter(Role.name == "日志管理员").first()
    role5 = session.query(Role).filter(Role.name == "超级管理员").first()

    try:
        # 用户管理员：用户模块
        session.add(RoleAuth(role_id=role2.id, auth_id=auth_module9.id))
        # 视频管理员：评论模块，视频模块，番剧模块，轮播图模块，标签模块
        session.add(RoleAuth(role_id=role3.id, auth_id=auth_module5.id))
        session.add(RoleAuth(role_id=role3.id, auth_id=auth_module10.id))
        session.add(RoleAuth(role_id=role3.id, auth_id=auth_module4.id))
        session.add(RoleAuth(role_id=role3.id, auth_id=auth_module2.id))
        session.add(RoleAuth(role_id=role3.id, auth_id=auth_module8.id))
        # 日志管理员：日志模块
        session.add(RoleAuth(role_id=role4.id, auth_id=auth_module6.id))
        # 超级管理员：所有模块
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module1.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module2.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module3.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module4.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module5.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module6.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module7.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module8.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module9.id))
        session.add(RoleAuth(role_id=role5.id, auth_id=auth_module10.id))
        session.commit()
    except Exception as e:
        session.rollback()


def generate_role():
    """生成角色模块"""
    session = Session()
    try:
        role1 = Role(id=1, name="普通用户")  # 普通用户
        role2 = Role(id=2, name="用户管理员")  # 用户管理员
        role3 = Role(id=3, name="视频管理员")  # 视频管理员
        role4 = Role(id=4, name="日志管理员")  # 日志管理员
        role5 = Role(id=5, name="超级管理员")  # 超级管理员
        session.add(role1)
        session.add(role2)
        session.add(role3)
        session.add(role4)
        session.add(role5)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()


def generate_user():
    """生成用户"""
    session = Session()
    # 父类
    try:
        baseuser1 = BaseUser()
        baseuser1.name = "user"
        baseuser1.gender = GenderEnum.MALE.value,
        baseuser1.account = 100
        baseuser1.pwd = 100
        session.add(baseuser1)
        session.commit()
        baseuser1 = session.query(BaseUser).filter(BaseUser.name == "user").first()
        # 子类
        user1 = User()
        user1.id = baseuser1.id
        user1.email = "1004901361@qq.com"
        user1.phone = "1367758064"
        session.add(user1)
        session.commit()
        # 子类
        admin1 = Admin()
        admin1.id = baseuser1.id
        session.add(admin1)
        session.commit()
    except Exception as e:
        print("添加user失败")
        session.rollback()

    try:
        # 父类
        baseuser2 = BaseUser()
        baseuser2.name = "user_admin"
        baseuser2.gender = GenderEnum.UNKNOWN.value,
        baseuser2.account = 200
        baseuser2.pwd = 200
        session.add(baseuser2)
        session.commit()
        baseuser2 = session.query(BaseUser).filter(BaseUser.name == "user_admin").first()
        # 子类
        admin2 = Admin()
        admin2.id = baseuser2.id
        session.add(admin2)
        session.commit()
    except Exception as e:
        print("添加user_admin失败")
        session.rollback()

    try:
        # 父类
        baseuser3 = BaseUser()
        baseuser3.name = "admin"
        baseuser3.gender = GenderEnum.MALE.value,
        baseuser3.account = 300
        baseuser3.pwd = 300
        session.add(baseuser3)
        session.commit()
        baseuser3 = session.query(BaseUser).filter(BaseUser.name == "admin").first()
        # 子类
        admin3 = Admin()
        admin3.id = baseuser3.id
        session.add(admin3)
        session.commit()
    except Exception as e:
        print("添加admin失败")
        session.rollback()

    try:
        # 父类
        baseuser4 = BaseUser()
        baseuser4.name = "log_admin"
        baseuser4.gender = GenderEnum.MALE.value,
        baseuser4.account = 400
        baseuser4.pwd = 400
        session.add(baseuser4)
        session.commit()
        baseuser4 = session.query(BaseUser).filter(BaseUser.name == "log_admin").first()
        # 子类
        admin4 = Admin()
        admin4.id = baseuser4.id
        session.add(admin4)
        session.commit()
    except Exception as e:
        print("添加log_admin失败")
        session.rollback()

    try:
        # 父类
        baseuser5 = BaseUser()
        baseuser5.name = "super_admin"
        baseuser5.gender = GenderEnum.FEMALE.value,
        baseuser5.account = 500
        baseuser5.pwd = 500
        session.add(baseuser5)
        session.commit()
        baseuser5 = session.query(BaseUser).filter(BaseUser.name == "super_admin").first()
        # 子类
        admin5 = Admin()
        admin5.id = baseuser5.id
        session.add(admin5)
        session.commit()
    except Exception as e:
        print("添加super_admin失败")
        session.rollback()

    """生成角色模块"""
    try:
        role1 = Role(id=1, name="普通用户")  # 普通用户
        role2 = Role(id=2, name="用户管理员")  # 用户管理员
        role3 = Role(id=3, name="视频管理员")  # 视频管理员
        role4 = Role(id=4, name="日志管理员")  # 日志管理员
        role5 = Role(id=5, name="超级管理员")  # 超级管理员
        session.add(role1)
        session.add(role2)
        session.add(role3)
        session.add(role4)
        session.add(role5)
        session.commit()
    except Exception as e:
        session.rollback()

    """用户角色关联"""
    try:
        session.add(UserRole(user_id=baseuser1.id, role_id=role1.id))
        session.add(UserRole(user_id=baseuser1.id, role_id=role5.id))
        session.add(UserRole(user_id=baseuser2.id, role_id=role2.id))
        session.add(UserRole(user_id=baseuser3.id, role_id=role3.id))
        session.add(UserRole(user_id=baseuser4.id, role_id=role4.id))
        session.add(UserRole(user_id=baseuser5.id, role_id=role5.id))
        session.commit()
    except Exception as e:
        session.rollback()


def generate_tag():
    """生成标签"""
    session = Session()

    # 一级标签
    tag_1 = Tag(id=id_generator.get_tag_id(), name="动画", parent_id=0, info="动画")
    tag_2 = Tag(id=id_generator.get_tag_id(), name="番剧", parent_id=0, info="番剧")
    tag_3 = Tag(id=id_generator.get_tag_id(), name="国创", parent_id=0, info="国创")
    tag_4 = Tag(id=id_generator.get_tag_id(), name="音乐", parent_id=0, info="音乐")
    tag_5 = Tag(id=id_generator.get_tag_id(), name="舞蹈", parent_id=0, info="舞蹈")
    tag_6 = Tag(id=id_generator.get_tag_id(), name="游戏", parent_id=0, info="游戏")
    tag_7 = Tag(id=id_generator.get_tag_id(), name="科技", parent_id=0, info="科技")
    tag_8 = Tag(id=id_generator.get_tag_id(), name="数码", parent_id=0, info="数码")
    tag_9 = Tag(id=id_generator.get_tag_id(), name="生活", parent_id=0, info="生活")
    tag_10 = Tag(id=id_generator.get_tag_id(), name="鬼畜", parent_id=0, info="鬼畜")
    tag_11 = Tag(id=id_generator.get_tag_id(), name="时尚", parent_id=0, info="时尚")
    tag_12 = Tag(id=id_generator.get_tag_id(), name="娱乐", parent_id=0, info="娱乐")
    tag_13 = Tag(id=id_generator.get_tag_id(), name="影视", parent_id=0, info="影视")
    session.add(tag_1)
    session.add(tag_2)
    session.add(tag_3)
    session.add(tag_4)
    session.add(tag_5)
    session.add(tag_6)
    session.add(tag_7)
    session.add(tag_8)
    session.add(tag_9)
    session.add(tag_10)
    session.add(tag_11)
    session.add(tag_12)
    session.add(tag_13)
    session.commit()
    # 二级标签
    session.add(Tag(name="MAD·AMV", parent_id=tag_1.id, info="具有一定制作程度的动画或静画的二次创作视频"))
    session.add(Tag(name="MMD·3D", parent_id=tag_1.id, info="使用MMD（MikuMikuDance）和其他3D建模类软件制作的视频"))
    session.add(Tag(name="短片·手书·配音", parent_id=tag_1.id, info="追求创新并具有强烈特色的短片、手书（绘）及ACG相关配音"))
    session.add(Tag(name="综合", parent_id=tag_1.id, info="动画以及动画相关内容为素材，包括但不仅限于音频替换、杂谈、排行榜等内容"))

    session.add(Tag(name="连载动画", parent_id=tag_2.id, info="连载动画"))
    session.add(Tag(name="完结动画", parent_id=tag_2.id, info="完结动画"))
    session.add(Tag(name="资讯", parent_id=tag_2.id, info="资讯"))
    session.add(Tag(name="官方延伸", parent_id=tag_2.id, info="官方延伸"))

    session.add(Tag(name="国产动画", parent_id=tag_3.id, info="国产动画"))
    session.add(Tag(name="国产原创相关", parent_id=tag_3.id, info="国产原创相关"))
    session.add(Tag(name="动态漫·广播剧", parent_id=tag_3.id, info="动态漫·广播剧"))
    session.add(Tag(name="资讯", parent_id=tag_3.id, info="资讯"))

    session.add(Tag(name="原创音乐", parent_id=tag_4.id, info="个人或团队制作以音乐为主要原创因素的歌曲或纯音乐"))
    session.add(Tag(name="翻唱", parent_id=tag_4.id, info="一切非官方的人声再演绎歌曲作品"))
    session.add(Tag(name="VOCALOID·UTAU", parent_id=tag_4.id, info="以雅马哈Vocaloid和UTAU引擎为基础，包含其他调教引擎，运用各类音源进行的歌曲创作内容"))
    session.add(Tag(name="电音", parent_id=tag_4.id, info="以电子合成器、音乐软体等产生的电子声响制作的音乐"))
    session.add(Tag(name="演奏", parent_id=tag_4.id, info="传统或非传统乐器及器材的演奏作品"))
    session.add(Tag(name="MV", parent_id=tag_4.id, info="音乐录影带，官方为搭配音乐而拍摄的短片"))
    session.add(Tag(name="音乐现场", parent_id=tag_4.id, info="音乐实况表演视频"))
    session.add(Tag(name="音乐综合", parent_id=tag_4.id, info="收录无法定义到其他音乐子分区的音乐视频"))
    session.add(Tag(name="音频", parent_id=tag_4.id, info="音频"))

    session.add(Tag(name="宅舞", parent_id=tag_5.id, info="与ACG相关的翻跳、原创舞蹈"))
    session.add(Tag(name="三次元舞蹈", parent_id=tag_5.id, info="以三次元音乐作为BGM的舞蹈"))
    session.add(Tag(name="舞蹈教程", parent_id=tag_5.id, info="镜面慢速，动作分解，基础教程等具有教学意义的舞蹈视频"))

    session.add(Tag(name="单机游戏", parent_id=tag_6.id, info="以所有平台（PC、主机、移动端）的单机或联机游戏为主的视频内容，"
                                                          "包括游戏预告、CG、实况解说及相关的评测、杂谈与视频剪辑等"))
    session.add(Tag(name="电子竞技", parent_id=tag_6.id, info="具有高对抗性的电子竞技游戏项目，其相关的赛事、实况、攻略、解说、短剧等视频"))
    session.add(Tag(name="手机游戏", parent_id=tag_6.id, info="以手机及平板设备为主要平台的游戏，其相关的实况、攻略、解说、短剧、演示等视频"))
    session.add(Tag(name="网络游戏", parent_id=tag_6.id, info="由网络运营商运营的多人在线游戏，以及电子竞技的相关游戏内容。包括赛事、攻略、实况、解说等相关视频"))
    session.add(Tag(name="桌游棋牌", parent_id=tag_6.id, info="桌游、棋牌、卡牌对战等及其相关电子版游戏的实况、攻略、解说、演示等视频"))
    session.add(Tag(name="GMV", parent_id=tag_6.id, info="由游戏素材制作的MV视频。以游戏内容或CG为主制作的，具有一定创作程度的MV类型的视频"))
    session.add(Tag(name="音游", parent_id=tag_6.id, info="各个平台上，通过配合音乐与节奏而进行的音乐类游戏视频"))
    session.add(Tag(name="Mugen", parent_id=tag_6.id, info="以Mugen引擎为平台制作、或与Mugen相关的游戏视频"))

    session.add(Tag(name="趣味科普人文", parent_id=tag_7.id, info="含有科普或人文性质的视频"))
    session.add(Tag(name="野生技术协会", parent_id=tag_7.id, info="展示一定改装/创作能力的视频"))
    session.add(Tag(name="演讲·公开课", parent_id=tag_7.id, info="演讲、教育课程相关的视频"))
    session.add(Tag(name="星海", parent_id=tag_7.id, info="军事相关视频"))
    session.add(Tag(name="机械", parent_id=tag_7.id, info="机械设备展示或制作视频"))
    session.add(Tag(name="汽车", parent_id=tag_7.id, info="汽车、摩托车、公交车以及竞赛用车等轮式交通工具相关"))

    session.add(Tag(name="手机平板", parent_id=tag_8.id, info="手机平板设备相关视频"))
    session.add(Tag(name="电脑装机", parent_id=tag_8.id, info="电脑装机及配件等相关视频"))
    session.add(Tag(name="摄影摄像", parent_id=tag_8.id, info="摄影摄像器材等相关视频"))
    session.add(Tag(name="影音智能", parent_id=tag_8.id, info="影音设备、智能产品等相关视频"))

    session.add(Tag(name="搞笑", parent_id=tag_9.id, info="搞笑的、轻松有趣的、具有独特笑点或娱乐精神的视频"))
    session.add(Tag(name="日常", parent_id=tag_9.id, info="漫展、cosplay、体育运动及其他一般日常向视频"))
    session.add(Tag(name="美食圈", parent_id=tag_9.id, info="美食鉴赏&料理制作教程"))
    session.add(Tag(name="动物圈", parent_id=tag_9.id, info="这里有各种萌萌哒动物哦~"))
    session.add(Tag(name="手工", parent_id=tag_9.id, info="简易手工艺品的diy制作视频，例如；折纸、手账、橡皮章等"))
    session.add(Tag(name="绘画", parent_id=tag_9.id, info="绘画爱好者们关于绘画技巧、绘图过程的分享交流场所"))
    session.add(Tag(name="运动", parent_id=tag_9.id, info="一般向运动项目以及惊险刺激的户外极限运动"))
    session.add(Tag(name="其他", parent_id=tag_9.id, info="对于分区归属不明的视频进行归纳整合的特定分区"))

    session.add(Tag(name="鬼畜调教", parent_id=tag_10.id, info="使用素材在音频、画面上做一定处理，达到与BGM一定的同步感"))
    session.add(Tag(name="音MAD", parent_id=tag_10.id, info="使用素材音频进行一定的二次创作来达到还原原曲的非商业性质稿件"))
    session.add(Tag(name="人力VOCALOID", parent_id=tag_10.id, info="将人物或者角色的无伴奏素材进行人工调音，使其就像VOCALOID一样歌唱的技术"))
    session.add(Tag(name="教程演示", parent_id=tag_10.id, info="鬼畜相关的教程演示"))

    session.add(Tag(name="美妆", parent_id=tag_11.id, info="涵盖妆容、发型、美甲等教程，彩妆、护肤相关产品测评、分享等"))
    session.add(Tag(name="服饰", parent_id=tag_11.id, info="服饰风格、搭配技巧相关的展示和教程视频"))
    session.add(Tag(name="健身", parent_id=tag_11.id, info="器械、有氧、拉伸运动等，以达到强身健体、减肥瘦身、形体塑造目的"))
    session.add(Tag(name="T台", parent_id=tag_11.id, info="发布会走秀现场及模特相关时尚片、采访、后台花絮"))
    session.add(Tag(name="风尚标", parent_id=tag_11.id, info="时尚明星专访、街拍、时尚购物相关知识科普"))

    session.add(Tag(name="综艺", parent_id=tag_12.id, info="国内外有趣的综艺和综艺相关精彩剪辑"))
    session.add(Tag(name="明星", parent_id=tag_12.id, info="娱乐圈动态、明星资讯相关"))
    session.add(Tag(name="Korea相关", parent_id=tag_12.id, info="Korea相关音乐、舞蹈、综艺等视频"))

    session.add(Tag(name="影视杂谈", parent_id=tag_13.id, info="影视评论、解说、吐槽、科普等"))
    session.add(Tag(name="影视剪辑", parent_id=tag_13.id, info="对影视素材进行剪辑再创作的视频"))
    session.add(Tag(name="短片", parent_id=tag_13.id, info="追求自我表达且具有特色的短片"))
    session.add(Tag(name="预告·资讯", parent_id=tag_13.id, info="影视类相关资讯，预告，花絮等视频"))
    session.add(Tag(name="特摄", parent_id=tag_13.id, info="特摄相关衍生视频"))

    session.commit()


def generate_video():
    """生成视频模块"""
    session = Session()


def generate_comment():
    """生成评论"""
    session = Session()
    # 生成一级评论
    session.add(Comment(video_id=1001, user_id=random.randint(1, 99), content="还行、能接受"))
    session.add(Comment(video_id=1001, user_id=random.randint(1, 99), content="水水水"))
    session.commit()

    # 生成二级评论
    tmp = []
    for i in session.query(Comment).all():
        tmp.append(i.id)
        session.add(Comment(root_id=i.id, video_id=1001, user_id=random.randint(1, 99), content="我也觉得"))
        session.add(Comment(root_id=i.id, video_id=1001, user_id=random.randint(1, 99), content="加我一个、水水水"))
    session.commit()

    # 生成回复评论
    for i in session.query(Comment).filter(Comment.root_id == None).all():
        for j in tmp:
            session.add(Comment(parent_id=i.id, root_id=j, video_id=1001,
                                user_id=random.randint(1, 99), content="别水了"))
            session.add(Comment(parent_id=i.id, root_id=j, video_id=1001,
                                user_id=random.randint(1, 99), content="狼洲牛逼"))
    session.commit()


def generate_follow():
    """关注生成"""
    session = Session()
    for i in session.query(BaseUser).all():
        if i.id != 6666:
            session.add(Follow(user_id=i.id, follow_id=6666))
    for i in range(10):
        session.add(Follow(user_id=6666, follow_id=random.randint(1, 99)))
    session.commit()


def test():
    """给图片加上https://"""
    engine = create_engine("mysql+pymysql://qw:qw@971230@134.175.93.183:3306/pilipili")
    Session = sessionmaker(bind=engine)
    session = Session()
    for i in session.query(Video).filter(Video.url != None).all():
        if "localhost" in i.url:
            i.url = i.url.replace("localhost", "134.175.93.183")
            session.add(i)
    session.commit()
    # for i in session.query(Bangumi).all():
    #     if i.logo.startswith("//") or i.logo.startswith("https://") or i.logo.startswith("http://"):
    #         continue
    #     else:
    #         i.logo = "https://" + i.logo
    #     session.add(i)
    # for i in session.query(Video).all():
    #     if i.logo.startswith("//") or i.logo.startswith("https://") or i.logo.startswith("http://"):
    #         continue
    #     else:
    #         i.logo = "https://" + i.logo
    #     session.add(i)
    # session.commit()
    # for i in session.query(Video).all():
    #     i.score = i.playnum * 0.8 + i.commentnum * 0.5 + i.danmunum * 0.5 + i.colnum * 1
    #     session.add(i)
    # session.commit()
    # for i in session.query(Bangumi).all():
    #     i.grade = i.score
    #     i.score = i.playnum * 0.8 + i.commentnum * 0.5 + i.danmunum * 0.5 + i.colnum * 1
    #     session.add(i)
    # session.commit()
    # for i in session.query(Bangumi).order_by(Bangumi.create_time.asc()).limit(30).all():
    #     session.add(BangumiCol(bangumi_id=i.id, user_id=6666))
    # session.commit()
    #
    # for i in session.query(Video).order_by(Video.create_time.asc()).limit(30):
    #     session.add(VideoCol(video_id=i.id, user_id=6666))
    # session.commit()


if __name__ == "__main__":
    # init()
    # generate_tag()
    # generate_user()
    # generate_follow()
    # generate_comment()
    # test()
    # generate_auth_module()
    # generate_user()
    test()
