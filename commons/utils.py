from commons.enums import UnderlyingDataFormat
from commons.modules import re, os, pd, time, json, datetime, timedelta
from commons.constants import HOLIDAY_DATA_PATH, DATA_PATH
 
MONTH_SET={
    1:'JAN',
    2:'FEB',
    3:'MAR',
    4:'APR',
    5:'MAY',
    6:'JUN',
    7:'JUL',
    8:'AUG',
    9:'SEP',
    10:'OCT',
    11:'NOV',
    12:'DEC'
}


def load_data(backtest_config):

    OVERALL_RESULT = []

    FROM_DATE = backtest_config.FROM_DATE
    TO_DATE = backtest_config.TO_DATE
    START_TIME = datetime.strptime(backtest_config.START_TIME,'%H:%M').time()
    END_TIME = datetime.strptime(backtest_config.END_TIME,'%H:%M').time()
    UNDERLYING = backtest_config.UNDERLYING_SYMBOL

    # UNDERLYING = 'BANKNIFTY'

    FINAL_DATA_SET = []

    FROM_DATE = datetime.strptime(FROM_DATE, '%Y-%m-%d').date()
    TO_DATE = datetime.strptime(TO_DATE, '%Y-%m-%d').date()

    # reference_date = datetime.today()
    

    DATA_RANGE = pd.date_range(FROM_DATE, TO_DATE)
    

    for CURRENT_DATE in DATA_RANGE:

        current_time = datetime.combine(CURRENT_DATE, START_TIME)
        end_time = datetime.combine(CURRENT_DATE, END_TIME)
        
        FORMATTED_DATE = CURRENT_DATE.strftime('%d%m%Y')
        MONTH_NUM = CURRENT_DATE.month
        MONTH = MONTH_SET.get(MONTH_NUM)

        FILE_PATH = fr'{DATA_PATH}\{MONTH}\{UNDERLYING}\{UnderlyingDataFormat.BANKNIFTY.value}{FORMATTED_DATE}.feather'
       
       
        if os.path.exists(FILE_PATH):
        
            if UNDERLYING == 'BANKNIFTY':
                DATASET = pd.read_feather(FILE_PATH)
                
                # Create WeeklyExpiry for the Underlying 
                EXPIRY_LST  = create_expiry(DATASET)
                SORTED_EXP_DATES = sorted(set(datetime.strptime(val, '%d%b%y') for val in EXPIRY_LST))
                weekly_expiry = (SORTED_EXP_DATES[0]).date()

                DATASET.loc[DATASET['Symbol']=='BANKNIFTY-I', 'WeeklyExpiry'] = weekly_expiry
                
                # ITERATING OVER DATE-TIME
                while current_time.time() <= end_time.time():

                    # Adding leg conditions:
                    for leg_key, leg_value in backtest_config.LEGS.items():

                        TRADE_OPTION = leg_value.get('TRADEOPTION', 'PE')
                        STRIKE_TYPE = leg_value.get('STRIKE_TYPE','ATM')

                        UNDERLYING_SYMBOL = create_symbol(DATASET, START_TIME, UNDERLYING, TRADE_OPTION, STRIKE_TYPE)

                        # TO GET THE UNDERLYING SYMBOL DATE FROM FROM-DATE TO TO-DATE. 
                        DATA_ROW = DATASET.loc[
                                    (DATASET['Symbol'] == UNDERLYING_SYMBOL) & 
                                    (DATASET['Time'] == current_time.time()) 
                                ]
                        # print(DATA_ROW)
                        # TO GET TARGET STOPLOSS FOR LEG  
                        IS_TARGET = leg_value.get('IS_TARGET', False)
                        TARGET = leg_value.get('TARGET', None)
                        IS_STOPLOSS = leg_value.get('IS_STOPLOSS', False)
                        STOPLOSS = leg_value.get('STOPLOSS', None)
        
                        FINAL_DATA_SET = check_target_and_stoploss(DATA_ROW, IS_TARGET, TARGET, IS_STOPLOSS, STOPLOSS, backtest_config.STRATEGY_LVL_TARGET, backtest_config.STRATEGY_LVL_SL)

                        OVERALL_RESULT.extend(FINAL_DATA_SET)

                    current_time += timedelta(minutes=1)

        else:
            continue
    
   
    return OVERALL_RESULT

def check_holiday(HOLIDAY_YEAR, GIVEN_DATE):
    CHECK_DATE = datetime.strptime(GIVEN_DATE, '%Y-%m-%d').date()

    HOLIDAY_DATASET = pd.read_feather(f'{HOLIDAY_DATA_PATH}\\{HOLIDAY_YEAR}.feather')

    DATE_LIST = [datetime.strptime(str(row['Date']),'%y%m%d').date() for index, row in HOLIDAY_DATASET.iterrows()]

    if CHECK_DATE in DATE_LIST:
        return True
    else:
        return False


def check_expiry(TRADING_SYMBOL):
    ...


def create_expiry(DATA_SET):
   
    EXPRIY_LST = []

    DISTINCT_SYMBOLS = pd.Series(DATA_SET['Symbol']).unique()
    
    for items in DISTINCT_SYMBOLS:
        if items == 'BANKNIFTY-I' or items == 'BANKNIFTY-II' or items == "BANKNIFTY-III":
            continue

        else:
            MATCH_DATA = re.search(r'\d{2}[A-Za-z]{3}\d{2}', items)

            if MATCH_DATA:
                EXPIRY_DATES = MATCH_DATA.group(0)
                EXPRIY_LST.append(EXPIRY_DATES)

            else:
                print(None)

    return EXPRIY_LST

# CREATE SYMBOL AS PER THE TIME AND EXPIRY
def create_symbol(DATA_SET, START_TIME, UNDERLYING, TRADE_OPTION, STRIKE_TYPE):
    UNDERLYING = 'BANKNIFTY'
    DATA_SET = pd.DataFrame(DATA_SET)
    
    DATA_ROW = DATA_SET.loc[(DATA_SET['Symbol'] == 'BANKNIFTY-I') & 
                            (DATA_SET['Time'].apply(lambda x: x if isinstance(x, time) else datetime.strptime(x, '%H:%M').time())==START_TIME)
                        ]

    ROUND_OFF_VALUE = round_off(DATA_ROW['Open'], UNDERLYING)

    STRIKE_PRICE = strike_type(STRIKE_TYPE, ROUND_OFF_VALUE, UNDERLYING, TRADE_OPTION)

    EXPIRY = (DATA_ROW['WeeklyExpiry'][0].strftime('%d%b%y').upper())

    UNDERLYING_SYMBOL = fr"{UNDERLYING}{EXPIRY}{STRIKE_PRICE}{TRADE_OPTION}"

    return UNDERLYING_SYMBOL
    

# ROUND OF THE VALUE AS PER THE UNDERLYING
def round_off(STRIKE_PRICE, UNDERLYING):
    if isinstance(STRIKE_PRICE, pd.Series):
        STRIKE_PRICE = STRIKE_PRICE.iloc[0]

    if UNDERLYING == 'BANKNIFTY':
        ROUND_STRIKE_PRICE = int(round(STRIKE_PRICE, -2))
        ...
    elif UNDERLYING == 'NIFTY':
        ...
    
    else:
        ...
    
    return ROUND_STRIKE_PRICE


def generate_result(FINAL_DATA_SET, LOT_SIZE, GET_QTY, TRADE_OPTION):
    FINAL_RESULT = []

    for items in FINAL_DATA_SET:
        FINAL_RESULT.append({
            "symbol":items['Symbol'].iloc[0],
            "date":datetime.strftime(items['Date'].iloc[0],"%Y-%m-%d"),
            "entry_time":items['Time'].iloc[0].strftime('%I:%M'),
            "exit_time":items['Time'].iloc[-1].strftime('%I:%M'),
            "entry_price":float(items['Open'].iloc[0]),
            "exit_price":float(items['Close'].iloc[-1]),
            "option_type":TRADE_OPTION,
            "lot_size":int(LOT_SIZE),
            "pnl":int(GET_QTY) * (float(items['Close'].iloc[-1] - items['Open'].iloc[0]).__round__(2))
        })

    PNL_RESULT = json.dumps(FINAL_RESULT)
    return (PNL_RESULT)


def get_lot_number(UNDERLYING, LOT_SIZE):
    if UNDERLYING == 'BANKNIFTY':
        QTY = int(LOT_SIZE) * 30
    elif UNDERLYING == 'NFITY':
        QTY = int(LOT_SIZE) * 75
    
    else:
        QTY = None

    return QTY


def check_target_and_stoploss(DATA_SET, IS_TARGET, TARGET_VALUE, IS_STOPLOSS, STOPLOSS_VALUE, STRATEGY_LVL_TG, STRATEGY_LVL_SL):
    RESULT_SET = []     
    
    if IS_TARGET == False and IS_STOPLOSS == False:
        return DATA_SET


    # for df in DATA_SET:

    TARGET_HIT = False
    STOPLOSS_HIT = False
    # exit_outer_loop = False

    for index, items in DATA_SET.iterrows():
        
        if ((IS_TARGET == True) and (IS_STOPLOSS == False) and (not TARGET_HIT)):
            if items['High'] >= (float(DATA_SET['High'].iloc[0]) + int(TARGET_VALUE)):
                RESULT_SET.append(DATA_SET.loc[:index+1])
                TARGET_HIT = True
          
                
                break
            
        if ((IS_STOPLOSS == True) and (IS_TARGET == False) and (not STOPLOSS_HIT)):
            if items['Low'] <= (float(DATA_SET['Low'].iloc[0]) - int(STOPLOSS_VALUE)):
                RESULT_SET.append(DATA_SET.loc[:index+1])
                STOPLOSS_HIT = True
               
                
                break
        
        
        if ((IS_TARGET == True) and (IS_STOPLOSS == True) and (not TARGET_HIT) and (not STOPLOSS_VALUE)):
                
                if items['High'] >= (float(DATA_SET['High'].iloc[0]) + int(TARGET_VALUE)):
                    RESULT_SET.append(DATA_SET.loc[:index+1])
                    TARGET_HIT = True
                   
                    
                    break

                if items['Low'] <= (float(DATA_SET['Low'].iloc[0]) - int(STOPLOSS_VALUE)):
                    RESULT_SET.append(DATA_SET.loc[:index+1])
                    STOPLOSS_HIT = True
                   
                    break
                

    if not TARGET_HIT and not STOPLOSS_HIT:
        RESULT_SET.append(DATA_SET)
    


    return RESULT_SET


def strike_type(STRIKE_TYPE, ROUND_OFF_VALUE, UNDERLYING, TRADE_OPTION):

    PATTERN = r'(OTM|ITM)-(\d+)'

    MATCH = re.match(PATTERN,STRIKE_TYPE)
    if MATCH:
        
        strike = MATCH.group(1)
        strike_number = MATCH.group(2)
    
    if UNDERLYING == 'BANKNIFTY':

        if strike == 'OTM' and TRADE_OPTION == 'CE':
            STRIKE_PRICE = ROUND_OFF_VALUE + (int(strike_number)*(100))
        
        elif strike =='OTM' and TRADE_OPTION =='PE':
            STRIKE_PRICE = ROUND_OFF_VALUE - (int(strike_number)*(100))

        elif strike == 'ITM' and TRADE_OPTION == 'PE':
            STRIKE_PRICE = ROUND_OFF_VALUE + (int(strike_number)*(100))
        
        elif strike == 'ITM' and TRADE_OPTION == 'CE':
            STRIKE_PRICE = ROUND_OFF_VALUE - (int(strike_number)*(100))

        else:
            STRIKE_PRICE = ROUND_OFF_VALUE
    
    else:
        ...
    
    return STRIKE_PRICE

