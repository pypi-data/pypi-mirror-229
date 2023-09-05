import jwt


def validate(_token: str, secret_key: str) -> bool:
    """토큰 유효성 검사"""
    if not _token or not secret_key:
        return False
    if not isinstance(_token, str) or not isinstance(secret_key, str):
        return False
    return True


def token(_token: str, secret_key: str) -> dict:
    """토큰 검증"""
    # Bearer 가 포함된 경우 변경
    if "Bearer " in _token and len(_token.split("Bearer ")) == 2:
        _token = _token.split("Bearer ")[1]
    if validate(_token, secret_key):
        raise InvalidTokenFormat("Invalid token format")
    try:
        payload = jwt.decode(_token, secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise InvalidToken("Invalid token")
    return payload


class VerifyException(Exception):
    pass


class InvalidToken(VerifyException):
    pass


class InvalidTokenFormat(VerifyException):
    pass
