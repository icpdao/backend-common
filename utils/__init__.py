import datetime
import calendar


def check_size(size: float):
    if '.' in str(size) and len(str(size).split('.')[-1]) > 1:
        raise ValueError('SIZE NOT AVAILABLE')


def get_next_time(time_zone, last_at, time_day, time_hour):
    last_time = datetime.datetime.fromtimestamp(last_at + time_zone * 60)
    if time_day > last_time.day or (
            time_day == last_time.day and time_hour > last_time.hour):
        next_time = datetime.datetime.strptime(
            f"{last_time.year}-{last_time.month}-{time_day} {time_hour}",
            "%Y-%m-%d %H"
        )
    else:
        next_month = datetime.datetime(
            last_time.year, last_time.month,
            calendar.monthrange(last_time.year, last_time.month)[1]) + datetime.timedelta(days=1)
        next_time = datetime.datetime.strptime(
            f"{next_month.year}-{next_month.month}-{time_day} {time_hour}",
            "%Y-%m-%d %H"
        )
    next_at = next_time.timestamp() - time_zone * 60
    return next_at


if __name__ == '__main__':
    check_size(2.33)
    check_size(2.3)
    check_size(2)
    check_size(22)
    check_size(22.1)
    check_size(22.123)
