from commons.enums import UnderlyingDataFormat
from commons.modules import re, os, pd, time, date, json, datetime, timedelta
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

    TO_DATE = backtest_config.TO_DATE
    FROM_DATE = backtest_config.FROM_DATE
    UNDERLYING = backtest_config.UNDERLYING_SYMBOL
    END_TIME = parse_time(backtest_config.END_TIME)
    START_TIME = parse_time(backtest_config.START_TIME)

    FROM_DATE = parse_date(FROM_DATE)
    TO_DATE = parse_date(TO_DATE)

    DATA_RANGE = pd.date_range(FROM_DATE, TO_DATE)

    OVERALL_DATA_SET = []

    EXIT_OUTER_LOOOP = False
    

    for CURRENT_DATE in DATA_RANGE:

        HIT_LEGS = []

        current_time = datetime.combine(CURRENT_DATE, START_TIME)
        end_time = datetime.combine(CURRENT_DATE, END_TIME)
        
        FILE_PATH = get_data_file_path(CURRENT_DATE, UNDERLYING)
       
       
        if os.path.exists(FILE_PATH):
        
            if UNDERLYING == 'BANKNIFTY':
                DATASET = pd.read_feather(FILE_PATH)
                
                # Create WeeklyExpiry for the Underlying 
                EXPIRY_LST  = create_expiry(DATASET)
                SORTED_EXP_DATES = sorted(set(datetime.strptime(val, '%d%b%y') for val in EXPIRY_LST))
                weekly_expiry = (SORTED_EXP_DATES[0]).date()

                DATASET.loc[DATASET['Symbol']=='BANKNIFTY-I', 'WeeklyExpiry'] = weekly_expiry

                # ITERATING OVER DATE-TIME
                ARCHIVE_PNL  = 0
                while current_time.time() <= end_time.time():
                    LEG_PNL = 0
                    # Adding leg conditions:
                    for leg_key, leg_value in backtest_config.LEGS.items():

                        if any(leg_key in entry for entry in HIT_LEGS):
                            continue 

                        TRADE_OPTION = leg_value.get('TRADEOPTION', 'PE')
                        STRIKE_TYPE = leg_value.get('STRIKE_TYPE','ATM')

                        UNDERLYING_SYMBOL = create_symbol(DATASET, START_TIME, UNDERLYING, TRADE_OPTION, STRIKE_TYPE)

                        ENTRY_DATA =  DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)]
                        
                        # TO GET THE UNDERLYING SYMBOL DATE FROM FROM-DATE TO TO-DATE. 
                        DATA_ROW = DATASET.loc[
                                    (DATASET['Symbol'] == UNDERLYING_SYMBOL) & 
                                    (DATASET['Time'] == current_time.time()) 
                                ]
                        
                        # TO CALCULATE LEG PNL
                        start_index_row = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)]['Open'].iloc[0]
                        LEG_PNL += (int(DATA_ROW['Close'].iloc[0] - start_index_row))

                        # TO GET TARGET STOPLOSS FOR LEG
                        IS_TARGET = leg_value.get('IS_TARGET', False)
                        TARGET = leg_value.get('TARGET', None)
                        IS_STOPLOSS = leg_value.get('IS_STOPLOSS', False)
                        STOPLOSS = leg_value.get('STOPLOSS', None)
                        
                        is_target_hit, is_stoploss_hit = check_target_and_stoploss(DATA_ROW, IS_TARGET, TARGET, IS_STOPLOSS, STOPLOSS, ENTRY_DATA)
                        if is_target_hit:
                            
                            start_idx = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)].index
                            end_idx = DATASET.loc[(DATASET["Symbol"] == UNDERLYING_SYMBOL) & (DATASET["Time"] == current_time.time())].index

                            FINAL_DATA = DATASET.iloc[start_idx.item():end_idx.item()+1]
                            HIT_LEGS.append({leg_key: FINAL_DATA})
                            OVERALL_DATA_SET.append({leg_key: FINAL_DATA}) 

                            ARCHIVE_PNL += LEG_PNL                       

                        elif is_stoploss_hit:
                            
                            start_idx = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)].index
                            end_idx = DATASET.loc[(DATASET["Symbol"] == UNDERLYING_SYMBOL) & (DATASET["Time"] == current_time.time())].index

                            FINAL_DATA = DATASET.iloc[start_idx.item():end_idx.item()+1]
                            HIT_LEGS.append({leg_key: FINAL_DATA})
                            OVERALL_DATA_SET.append({leg_key: FINAL_DATA}) 

                            ARCHIVE_PNL += LEG_PNL

                        elif current_time.time() == end_time.time():
                            start_idx = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)].index
                            end_idx = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == current_time.time())].index

                            FINAL_DATA = DATASET.iloc[start_idx.item():end_idx.item()+1]
                            OVERALL_DATA_SET.append(FINAL_DATA)

                            ARCHIVE_PNL += LEG_PNL
                    
                    OVERALL_LEG_PNL = LEG_PNL * get_lot_number(UNDERLYING, backtest_config.LOT_SIZE)
                    OVERALL_LEG_PNL += ARCHIVE_PNL * get_lot_number(UNDERLYING, backtest_config.LOT_SIZE)
                    
                    if backtest_config.STRATEGY_LVL_TARGET[0] == True:
                        
                        if int(backtest_config.STRATEGY_LVL_TARGET[1]) < int(OVERALL_LEG_PNL):
                            EXIT_OUTER_LOOOP = True
                            print(f"STRATEGY LVL TARGET HIT: {backtest_config.STRATEGY_LVL_TARGET} : OVERALL_PNL: {OVERALL_LEG_PNL}")

                            for leg_key, leg_value in backtest_config.LEGS.items():

                                if any(leg_key in entry for entry in HIT_LEGS):
                                    continue

                                TRADE_OPTION = leg_value.get('TRADEOPTION', 'PE')
                                STRIKE_TYPE = leg_value.get('STRIKE_TYPE','ATM')

                                UNDERLYING_SYMBOL = create_symbol(DATASET, START_TIME, UNDERLYING, TRADE_OPTION, STRIKE_TYPE)
                                start_idx = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)].index
                                end_idx = DATASET.loc[(DATASET["Symbol"] == UNDERLYING_SYMBOL) & (DATASET["Time"] == current_time.time())].index

                                FINAL_DATA = DATASET.iloc[start_idx.item():end_idx.item()+1]
                                OVERALL_DATA_SET.append({leg_key: FINAL_DATA})

                            break 
                    
                    if backtest_config.STRATEGY_LVL_SL[0] == True:
                        
                        if -(int(backtest_config.STRATEGY_LVL_SL[1])) > int(OVERALL_LEG_PNL):
                            EXIT_OUTER_LOOOP = True
                            print(f"STRATEGY LVL SL HIT: {backtest_config.STRATEGY_LVL_SL} : OVERALL_PNL: {OVERALL_LEG_PNL} Current_Time: {current_time}")

                            for leg_key, leg_value in backtest_config.LEGS.items():

                                if any(leg_key in entry for entry in HIT_LEGS):
                                    continue    

                                TRADE_OPTION = leg_value.get('TRADEOPTION', 'PE')
                                STRIKE_TYPE = leg_value.get('STRIKE_TYPE','ATM')

                                UNDERLYING_SYMBOL = create_symbol(DATASET, START_TIME, UNDERLYING, TRADE_OPTION, STRIKE_TYPE)
                                start_idx = DATASET[(DATASET['Symbol'] == UNDERLYING_SYMBOL) & (DATASET['Time'] == START_TIME)].index
                                end_idx = DATASET.loc[(DATASET["Symbol"] == UNDERLYING_SYMBOL) & (DATASET["Time"] == current_time.time())].index

                                FINAL_DATA = DATASET.iloc[start_idx.item():end_idx.item()+1]
                                OVERALL_DATA_SET.append({leg_key: FINAL_DATA})

                            break

                    current_time += timedelta(minutes=1)

                if EXIT_OUTER_LOOOP == True:
                    continue
        else:
            continue
    
    
    return OVERALL_DATA_SET

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

    EXPIRY = (DATA_ROW['WeeklyExpiry'].iloc[0].strftime('%d%b%y').upper())

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

    # print(f"Final data set: {(FINAL_DATA_SET)}")

    for var in FINAL_DATA_SET:
        if type(var) == dict:
            for key, value in var.items():
                FINAL_RESULT.append({
                "symbol":value['Symbol'].iloc[0],
                "date":datetime.strftime(value['Date'].iloc[0],"%Y-%m-%d"),
                "entry_time":value['Time'].iloc[0].strftime('%I:%M'),
                "exit_time":value['Time'].iloc[-1].strftime('%I:%M'),
                "entry_price":float(value['Open'].iloc[0]),
                "exit_price":float(value['Close'].iloc[-1]),
                "option_type":TRADE_OPTION,
                "lot_size":int(LOT_SIZE),
                "pnl":int(GET_QTY) * (float(value['Close'].iloc[-1] - value['Open'].iloc[0]).__round__(2)),
                "exit_reason":""
            })
                    
        else:
            FINAL_RESULT.append({
                "symbol":var['Symbol'].iloc[0],
                "date":datetime.strftime(var['Date'].iloc[0],"%Y-%m-%d"),
                "entry_time":var['Time'].iloc[0].strftime('%I:%M'),
                "exit_time":var['Time'].iloc[-1].strftime('%I:%M'),
                "entry_price":float(var['Open'].iloc[0]),
                "exit_price":float(var['Close'].iloc[-1]),
                "option_type":TRADE_OPTION,
                "lot_size":int(LOT_SIZE),
                "pnl":int(GET_QTY) * (float(var['Close'].iloc[-1] - var['Open'].iloc[0]).__round__(2)),
                "exit_reason":""
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


def check_target_and_stoploss(DATA_SET, IS_TARGET, TARGET_VALUE, IS_STOPLOSS, STOPLOSS_VALUE, ENTRY_DATA):
    HIGH_VALUE =   ENTRY_DATA["High"].values[0]
    LOW_VALUE =   ENTRY_DATA["Low"].values[0]

    if IS_TARGET == False and IS_STOPLOSS == False:
        return None, None

    TARGET_HIT = False
    STOPLOSS_HIT = False

    if IS_TARGET:
        if not TARGET_HIT:
            if DATA_SET['High'].iloc[0] >= (float(HIGH_VALUE) + int(TARGET_VALUE)):
                TARGET_HIT = True
        

    if IS_STOPLOSS:
        if not STOPLOSS_HIT and (not TARGET_HIT):
            if DATA_SET['Low'].iloc[0] <= (float(LOW_VALUE) - int(STOPLOSS_VALUE)):
                STOPLOSS_HIT = True

    return TARGET_HIT, STOPLOSS_HIT

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



# CODE REFACTORING

def parse_date(date_str: str):
    """ Parse date string to Date time object. """

    return datetime.strptime(date_str,'%Y-%m-%d').date()

def parse_time(time_str: str):

    """ Parse time string to Time Object. """

    return datetime.strptime(time_str,'%H:%M').time()

def get_data_file_path(current_date: date, underlying: str) -> str:
    """ Generate file path for the given date """

    FORMATTED_DATE = current_date.strftime('%d%m%Y')
    MONTH_NUM = current_date.month
    MONTH = MONTH_SET.get(MONTH_NUM)

    return os.path.join(
        DATA_PATH,
        MONTH,
        underlying,
        f"{UnderlyingDataFormat.BANKNIFTY.value}{FORMATTED_DATE}.feather"
    )