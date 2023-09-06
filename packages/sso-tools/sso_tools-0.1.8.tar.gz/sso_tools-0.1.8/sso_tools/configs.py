import datetime


# JWT 알고리즘
JWT_ALGORITHMS = "HS256"
# 현재 시간
NOW = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))
