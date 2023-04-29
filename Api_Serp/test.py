from datetime import datetime
def diffrence_time(time,time_report):
    datetime_news = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
    datetime_report = datetime.strptime(time_report, '%Y-%m-%d %H:%M:%S.%f')

    timedelta = datetime_news - datetime_report
    return timedelta
time = '2023-04-29T13:28:14.990189'


time = time.replace('T', ' ')

time_report = '23-04-23 05:07:10.447200'
time_report = '20'+time_report

print(time)


print(diffrence_time(time,time_report) )