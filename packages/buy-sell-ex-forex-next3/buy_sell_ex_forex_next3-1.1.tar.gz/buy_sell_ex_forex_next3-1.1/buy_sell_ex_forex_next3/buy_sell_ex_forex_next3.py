import MetaTrader5 as mt5

from login_forex_next3 import Login

class BUY_SELL:

    def buy(symbol, lot, price , tp , deviation, magic , comment):

        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            # "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "comment": comment,
            "magic": magic,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK

        }

    def sell(symbol, lot, price, tp , deviation, magic, comment):

        return {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            # "sl": sl,
            "tp": tp,
            "deviation": deviation,
            "comment": comment,
            "magic": magic,
            "type_time": mt5.ORDER_TIME_GTC,  
            "type_filling": mt5.ORDER_FILLING_FOK,

        }

    def pos_buy(amount , lot , symbol_EURUSD , command):

      # try:
        
             infologin = Login.infologin(symbol_EURUSD)
             ask = infologin[3]
             print("ask:" , ask)
             point = mt5.symbol_info(symbol_EURUSD).point
             # sl = mt5.symbol_info_tick("EURUSD").ask - 1000 * point
             tp = mt5.symbol_info_tick("EURUSD").ask + amount * point
             
           #   filling_type = mt5.symbol_info(symbol_EURUSD).filling_mode
             request = BUY_SELL.buy(symbol_EURUSD , lot , ask , tp , 10 , 0  , command)
             result = mt5.order_send(request)
             # check the execution result
            #  print("result:" , result)
             execution = result.comment
             # position_ticket = result.order
     
             if execution == 'Request executed':
                 print("execution: buy true")


             return result    

          
      # except:
      #    print("error buy")
 
    def pos_sell(amount , lot , symbol_EURUSD , command):

      # try:
        
           infologin = Login.infologin(symbol_EURUSD)
           bid = infologin[4]
           
           print("bid:" , bid)
   
           point = mt5.symbol_info(symbol_EURUSD).point
   
           # sl = mt5.symbol_info_tick("EURUSD").ask - 100 * point
           tp = mt5.symbol_info_tick("EURUSD").bid - amount * point
           bid = infologin[4]
           request = BUY_SELL.sell(symbol_EURUSD, lot , bid , tp , 10 , 0, command )
           result = mt5.order_send(request)
           # check the execution result
           execution = result.comment
           # position_ticket = result.order
   
           if execution == 'Request executed':
               print("execution: sell true")

           return result      

      # except:
      #   print("error sell") 

    def update_buy(symbol_EURUSD , lot , ticket , tp):
        req = {
          "action": mt5.TRADE_ACTION_SLTP,
          "symbol": symbol_EURUSD,
          "volume": lot,
          "type": mt5.ORDER_TYPE_BUY,
          "position":ticket,
          "tp": tp,
          "deviation": 10,
          "comment": "BUY_ASlah",
          "magic": 234000,
          "type_time": mt5.ORDER_TIME_GTC,
          "type_filling": mt5.ORDER_FILLING_FOK
        }
        result = mt5.order_send(req)
        execution = result.comment
             # position_ticket = result.order
     
        if execution == 'Request executed':
              print("execution: Update_buy true")

