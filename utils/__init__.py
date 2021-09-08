import datetime
import calendar

from .errors import JOB_UPDATE_SIZE_INVALID_ERROR


def check_size(size: float):
    if '.' in str(size) and len(str(size).split('.')[-1]) > 1:
        raise ValueError(JOB_UPDATE_SIZE_INVALID_ERROR)


def get_next_time(time_zone, last_at, time_day, time_hour, can_eq=False):
    """
    time_zone 是时区数字
    last_at utc 时间戳
    time_day time_zone 下的时间 天
    time_hour time_zone 下的时间 小时
    result: time_zone 下一个 time_day time_hour 具体的 UTC 时间戳
    """
    last_time = datetime.datetime.fromtimestamp(last_at, tz=datetime.timezone(datetime.timedelta(minutes=time_zone)))
    is_eq = time_day == last_time.day and time_hour == last_time.hour
    is_gt = time_day > last_time.day or (time_day == last_time.day and time_hour > last_time.hour)
    if can_eq:
        flag = is_eq or is_gt
    else:
        flag = is_gt
    if flag:
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


if __name__ == '__main__':
    check_size(2.33)
    check_size(2.3)
    check_size(2)
    check_size(22)
    check_size(22.1)
    check_size(22.123)
