import datetime

latest_day = datetime.datetime.now(datetime.timezone.utc).date()

def hours_until_new_swipes():
    current_utc_time = datetime.datetime.now(tz=datetime.timezone.utc)
    tomorrow_utc_time = current_utc_time + datetime.timedelta(days=1)
    midnight_tomorrow = datetime.datetime(tomorrow_utc_time.year, tomorrow_utc_time.month, tomorrow_utc_time.day, tzinfo=datetime.timezone.utc)
    time_difference = midnight_tomorrow-current_utc_time
    hours_until_next_day = time_difference.total_seconds() / 3600
    return hours_until_next_day