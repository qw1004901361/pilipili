# coding=UTF-8
import datetime

# now_time = datetime.datetime.now()
# now_time = now_time.replace(hour=12, minute=0, second=0)
# before_time = now_time - datetime.timedelta(days=1)
#
# print(now_time.strftime("%Y-%m-%d %H:%M"))
# print(before_time.strftime("%Y-%m-%d %H:%M"))
# print(now_time.hour)
#
#
# def test(*args):
#     for i in args:
#         if 20 not in args:
#             a = (20,)
#             c = a + args
#     print(c)
#
#
# test(1, 2, 34)
# tmp = datetime.datetime.now().time()
# a = datetime.datetime.now().isoweekday()
# b = datetime.datetime.now().date()
# datetime.date.month
# print(b)
# print(a)
# print(type(a))
# print(tmp.replace(second=0, microsecond=0))
# from app.libs.enums import WeekEnum
#
# print(WeekEnum(1).name)

today_date = datetime.datetime.now().date()
for i in range(-6, 7):
    print(today_date + datetime.timedelta(days=i))
