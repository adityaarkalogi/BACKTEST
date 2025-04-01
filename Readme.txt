Run backtest

payload = {
    "start_date": xxx,
    "end_date": xxx,
    "strike_shift": 0 or 1 or -1,
    "start_time": xxx,
    "end_time": xxx,
    "expiry": "WEEKLY",or "NEXT_WEEKLY", or "MONTHLY"
    "trade_options": ["CE","PE"],
    "first_action": "BUIY",
    "qty": 25
}



-> loop -> from date to date -> check holiday -> check expiry as per the instrument type/ symbol NFO -> 
-> create expiry for BANKNIFTY-I -> update the dataframe/dataset with weekly expiry

result ={
    symbol:"",
    entry_time:"",
    exit_time:"",
    entry_price:"",
    exit_price:"",
    pnl:"",
    type:""
}

multiple legs => 

legs = {

    l1 : {
        is_target: 'y',
        target: '5',
        is_stoploss: 'y',
        stoploss: 2
    },

    l1 : {
        is_target: 'y',
        target: '5',
        is_stoploss: 'y',
        stoploss: 2
    },

}

-> trade trade_options-> multiple legs -> strike type 
1) OTM -CE ->Upper, PE-> Lower
2) ITM -> CE -> Lower, PE -> Upper

-> strategy level target stoploss
-> if the strategy has  TG/SL  

to get strategy lvl - sl/tg -> if tg is set it will check for the code without the legs and if it goes up it will sq off.