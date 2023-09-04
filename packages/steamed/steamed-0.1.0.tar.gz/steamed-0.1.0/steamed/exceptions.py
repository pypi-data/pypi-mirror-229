class SteampyException(Exception):
    """All the exception of this library should extend this."""

    def __init__(self, *args: object, data=None) -> None:
        super().__init__(*args)
        self.data = data


class TradeHoldException(SteampyException):
    pass


class TooManyRequests(SteampyException):
    pass


class ApiException(SteampyException):
    pass


class LoginRequired(SteampyException):
    pass


class CaptchaRequired(SteampyException):
    pass


class ConfirmationExpected(SteampyException):
    pass


class LoginException(SteampyException):
    pass


class InvalidCredentials(LoginException):
    pass


class SteamServerError(SteampyException):
    pass


class ParameterError(SteampyException):
    pass


# classful

class InvalidTradeOfferID(SteampyException):
    pass
