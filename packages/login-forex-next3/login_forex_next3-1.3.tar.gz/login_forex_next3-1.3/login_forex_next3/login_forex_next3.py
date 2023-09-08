import MetaTrader5 as Mt5
import json


class Tick:

    def __init__(self, symbol):

        self.time = Mt5.symbol_info_tick(symbol).time
        self.bid = Mt5.symbol_info_tick(symbol).bid
        self.ask = Mt5.symbol_info_tick(symbol).ask
        self.last = Mt5.symbol_info_tick(symbol).last
        self.volume = Mt5.symbol_info_tick(symbol).volume
        self.time_msc = Mt5.symbol_info_tick(symbol).time_msc
        self.flags = Mt5.symbol_info_tick(symbol).flags
        self.volume_real = Mt5.symbol_info_tick(symbol).volume_real

    def filling_type(input):

        if input == 1:
            return "Mt5.ORDER_FILLING_FOK"
        
        elif input == 2:
            return "ORDER_FILLING_IOC"
        
        elif input == 3:
            return "ORDER_FILLING_RETURN"

class Login:

    def __init__(self , Login , Server , Password):
        
        self.authorized = Mt5.initialize(
            login=Login, server=Server, password=Password)
        
        print("self.authorized:" , self.authorized)

        if self.authorized == True:
            print("connectbroker is ok")
  

    def __str__(self):
       return f"({self.authorized})"
    

    def infologin(self , symbol):

        if self.authorized == True:

            account_info = Mt5.account_info()

            if account_info != None:

                balance = account_info.balance
                equity = account_info.equity
                profit = account_info.profit
                
                ask = Tick(symbol).ask
                bid = Tick(symbol).bid

                return balance , equity , profit ,  ask , bid

            else:
                print("failed to connect to trade account , error code =",
                      Mt5.last_error())

        else:
            print("connectbroker is ok")


