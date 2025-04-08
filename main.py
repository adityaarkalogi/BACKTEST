import backtest
from commons.models import BACKTESTER

config = BACKTESTER(
    FROM_DATE = '2023-04-09',
    TO_DATE = '2023-04-13',
    START_TIME =  '09:30',
    END_TIME =  '12:15',
    UNDERLYING_SYMBOL =  'BANKNIFTY',
    TRADE_OPTION = 'CE',
    LOT_SIZE = '1',
    NO_OF_LEGS= '1',
    LEGS = {
        'L1' : {
            'IS_TARGET': False,
            'TARGET': 20,
            'IS_STOPLOSS': False,
            'STOPLOSS': 10,
            'TRADEOPTION':'CE',
            'STRIKE_TYPE': 'OTM-1',
        },

        'L2' : {
            'IS_TARGET': True,
            'TARGET': 999,
            'IS_STOPLOSS': True,
            'STOPLOSS': 999,
            'TRADEOPTION':'PE',
            'STRIKE_TYPE':'OTM-1',
        },
    },
    
    STRATEGY_LVL_TARGET = [False, 1000],
    STRATEGY_LVL_SL = [True, 1000]
)

backtest_result = backtest.run_backtest(config)

print(backtest_result)


