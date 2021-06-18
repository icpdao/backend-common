import datetime
import calendar


def check_size(size: float):
    if '.' in str(size) and len(str(size).split('.')[-1]) > 1:
        raise ValueError('SIZE NOT AVAILABLE')


def get_next_time(time_zone, last_at, time_day, time_hour):
    """
    time_zone 是时区数字
    last_at utc 时间戳
    time_day time_zone 下的时间 天
    time_hour time_zone 下的时间 小时
    result: time_zone 下一个 time_day time_hour 具体的 UTC 时间戳
    """
    last_time = datetime.datetime.fromtimestamp(last_at, tz=datetime.timezone(datetime.timedelta(minutes=time_zone)))
    if time_day > last_time.day or (
            time_day == last_time.day and time_hour > last_time.hour):
        next_datetime = datetime.datetime(
            year=last_time.year,
            month=last_time.month,
            day=time_day,
            hour=time_hour,
            tzinfo=last_time.tzinfo
        )
    else:
        next_month = datetime.datetime(
            year=last_time.year,
            month=last_time.month,
            day=calendar.monthrange(last_time.year, last_time.month)[1],
            tzinfo=last_time.tzinfo
        ) + datetime.timedelta(days=1)
        next_datetime = datetime.datetime(
            year=next_month.year,
            month=next_month.month,
            day=time_day,
            hour=time_hour,
            tzinfo=last_time.tzinfo
        )

    next_at = next_datetime.timestamp()
    return next_at


# def get_next_time(time_zone, last_at, time_day, time_hour):
#     """
#     time_zone 是时区数字
#     last_at utc 时间戳
#     time_day time_zone 下的时间 天
#     time_hour time_zone 下的时间 小时
#     result: time_zone 下下一个 time_day time_hour 具体的 UTC 时间戳
#     """
#     last_time = datetime.datetime.fromtimestamp(last_at + time_zone * 60)
#     if time_day > last_time.day or (
#             time_day == last_time.day and time_hour > last_time.hour):
#         next_time = datetime.datetime.strptime(
#             f"{last_time.year}-{last_time.month}-{time_day} {time_hour}",
#             "%Y-%m-%d %H"
#         )
#     else:
#         next_month = datetime.datetime(
#             last_time.year, last_time.month,
#             calendar.monthrange(last_time.year, last_time.month)[1]) + datetime.timedelta(days=1)
#         next_time = datetime.datetime.strptime(
#             f"{next_month.year}-{next_month.month}-{time_day} {time_hour}",
#             "%Y-%m-%d %H"
#         )
#     next_at = next_time.timestamp() - time_zone * 60
#     return next_at


if __name__ == '__main__':
    check_size(2.33)
    check_size(2.3)
    check_size(2)
    check_size(22)
    check_size(22.1)
    check_size(22.123)
