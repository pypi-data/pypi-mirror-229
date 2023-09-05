import jwt


def validate_token(credentials: str, secret_key: str) -> bool:
    """토큰 유효성 검사"""
    if not credentials:
        return False
    if not secret_key:
        return False
    if not isinstance(credentials, str):
        return False
    if "Bearer" not in credentials:
        return False
    if len(credentials.split(" ")) < 2:
        return False
    return True


def verify_token(credentials: str, secret_key: str) -> dict:
    """토큰 검증"""
    if validate_token(credentials, secret_key):
        raise InvalidTokenFormat("Invalid token format")
    try:
        token_value = credentials.split(" ")[1]
        payload = jwt.decode(token_value, secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise InvalidToken("Invalid token")
    return payload


class VerifyException(Exception):
    pass


class InvalidToken(VerifyException):
    pass


class InvalidTokenFormat(VerifyException):
    pass
