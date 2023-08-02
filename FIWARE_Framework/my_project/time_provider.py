import datetime
import pytz
class TimeProvider():
    def GetCurrentTime(self):
        today = datetime.datetime.now()
        today = today.replace(tzinfo=pytz.UTC)
        return today.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    def GetFutureTime(self, days):
        today = datetime.datetime.now()
        first = today.replace(day=1)
        future = first + datetime.timedelta(days)
        future = future.replace(tzinfo=pytz.UTC)
        return future.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    def GetPastTime(self, days):
        today = datetime.datetime.now()
        first = today.replace(day=1)
        past = first - datetime.timedelta(days)
        past = past.replace(tzinfo=pytz.UTC)
        return past.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
if __name__ == "__main__":
    time = TimeProvider()
    print(time.GetPastTime(10))