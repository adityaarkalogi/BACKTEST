import backtest
from commons.models import BACKTESTER

config = BACKTESTER(
    FROM_DATE = '2023-04-09',
    TO_DATE = '2023-04-11',
    START_TIME =  '09:30',
    END_TIME =  '10:15',
    UNDERLYING_SYMBOL =  'BANKNIFTY',
    TRADE_OPTION = 'CE',
    LOT_SIZE = '1',
    NO_OF_LEGS= '1',
    LEGS = {
        'L1' : {
            'IS_TARGET': True,
            'TARGET': 20,
            'IS_STOPLOSS': True,
            'STOPLOSS': 10,
            'TRADEOPTION':'CE',
            'STRIKE_TYPE': 'OTM-1',
        },

        'L2' : {
            'IS_TARGET': True,
            'TARGET': 5,
            'IS_STOPLOSS': True,
            'STOPLOSS': 2,
            'TRADEOPTION':'PE',
            'STRIKE_TYPE':'OTM-1',
        },
    },
    
    STRATEGY_LVL_TARGET = [True, 2000],
    STRATEGY_LVL_SL = [False, 0]
)

backtest_result = backtest.run_backtest(config)

print(backtest_result)


