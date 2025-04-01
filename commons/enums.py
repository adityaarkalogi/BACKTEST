import enum

class ExpiryType(enum.Enum):
    WEEKLY = 'WEEKLY'
    NEXTWEEKLY = 'NEXTWEEKLY'
    MONTHLY = 'MONTHLY'



class ExchangeType(enum.Enum):
    NFO = 'NFO'


class OptionType(enum.Enum):
    CE = 'CE'
    PE = 'PE'

class UnderlyingDataFormat(enum.Enum):
    BANKNIFTY = 'BANKNIFTY_JF_FNO_'
    NIFTY = 'NIFTY_JF_FNO_'