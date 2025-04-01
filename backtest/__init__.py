from commons.models import BACKTESTER
from commons.utils import load_data, get_lot_number, generate_result, check_target_and_stoploss

def run_backtest(backtest_config: BACKTESTER):
   
    FINAL_DATA_SET = load_data(backtest_config)

    GET_QTY = get_lot_number(backtest_config.UNDERLYING_SYMBOL, backtest_config.LOT_SIZE)

    return generate_result(FINAL_DATA_SET, backtest_config.LOT_SIZE, GET_QTY, backtest_config.TRADE_OPTION)