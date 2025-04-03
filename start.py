from_date = ""
to_date = ""

start_time = ""
end_time = ""

tgt = ""
sl = ""
sq_off = ""

stg_tgt= ""
stg_sl = ""

legs = []


for i in range(from_date, to_date):
    for j in range(start_time, end_time):
        stg_pnl = 0
        for l in legs:
            leg_pnl = ""
            if leg_pnl >= tgt:
                ...
                # leg_exit
            elif leg_pnl < sl:
                ...
                #leg_exit
            elif j >= sq_off:
                ...
                #leg_exit

            stg_pnl += leg_pnl

        if stg_pnl >= stg_tgt:
            ...
            #exit_all_legs
            for l in legs:
                #exit
                ...
        elif stg_pnl < stg_sl:
            #exit_all_legs
            for l in legs:
                #exit
                ...



    ########################################################################################

    for date in date_range:
        read_data(date_wise)
        while current_time <= end_time:
            for leg in leg_list:
                create_symbol
                check_target_stoploss
                
                if leg tgt or sl hit:
                    exit leg
            
            check_strategy_tgt_sl

            if yes:
                for leg in leg_list:
                    exit_all_legs

            increment_time
            
day => 2 days i.e. date 10-04-2023,  11-04-2024
time => 9:15 -> 3:15


