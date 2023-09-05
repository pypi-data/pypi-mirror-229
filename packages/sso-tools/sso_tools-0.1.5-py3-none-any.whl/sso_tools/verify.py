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
    if not validate(_token, secret_key):
        raise InvalidTokenFormat("Invalid Token Format")
    try:
        payload = jwt.decode(_token, secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise InvalidToken("Invalid Token")
    return payload


class VerifyException(Exception):
    """토큰 검증 오류"""
    pass


class InvalidTokenFormat(VerifyException):
    """토큰 포멧이 유효하지 않음"""
    pass


class InvalidToken(VerifyException):
    """토큰이 정상적이지 않음"""
    pass
