from bittrex import Bittrex, API_V2_0, API_V1_1
import math, time, datetime

my_bittrex1_1 = Bittrex("APIKEY", "APISECRET", api_version=API_V1_1)
balance2_0 = Bittrex("APIKEY", "APISECRET", api_version=API_V2_0)

def check_all_tradingsignal(result1, result2, result3):
  ### check all the trading signals ###
  ### (OK) ###
  resultall = 0
  if result1['result'] is None:
    resultall += 1
  elif result2['result'] is None:
    resultall += 1
  elif result3['result'] is None:
    resultall += 1
  else :
    resultall = 0

  return resultall

def check_tradingsignal(result):
  ### check signal singal ###
  ### (OK) ###
  result_check = 0
  if result['result'] is None:
    result_check = 1
  else:
    result_check = 0

  return result_check

def typecheck_trading_price(result):
  ### check the price is float ###
  ###(OK)###
  if type(result) is float:
    return 1
  else: 
    return 0

def check_none_balance(result):
  ### check balance ###
  ### (OK) ###
  result_check_balance = 0
  if result['result'] is None:
    result_check_balance = 1
  elif result['result']['Balance'] is None:
    result_check_balance = 1
  else :
    result_check_balance = 0

  return result_check_balance

def check_order(ordered_market):
  ### check the openorder, return its uuid ###
  ### (OK) ### 

  openorders = my_bittrex1_1.get_open_orders(ordered_market)
  uuid = str()

  if openorders['success'] is True:
    if openorders['result'] != []:
      uuid = openorders['result'][0]['OrderUuid']
    else:
      uuid = 'OrderUuidisGone' 
  else: 
    uuid = 'OrderUuidisGone'

  return uuid

def quantity_decision (money, price):
  ### check the quantity for currency ###
 i = 0
 unit = (money*0.9975) / price
 while 1:
  if math.floor(unit) !=0:
    unit = unit*(10)
    unit -= 1
    i+=1
    unit = unit * (10**(-i))
    unit = round(unit,i)
    break
  else :
    unit = unit*10
    i+=1
    continue

 return unit

def BTCprice_stability(BTC_ave, BTC_now):
  if 0.9975 < (BTC_now['result']['Ask']/BTC_ave) < 1.0025:
    return 0
  else:
    return 1

def BTCprice_average(BTC_ave, BTC_now):
  average = (BTC_ave + BTC_now['result']['Ask'])/2
  return average

def pricecheck_USDT(USDTworker_Ask, workerBTC_Bid, BTCtoUSDT_price):
  ### doubt ###
  if min(typecheck_trading_price(USDTworker_Ask['Ask']), typecheck_trading_price(workerBTC_Bid['Bid']), typecheck_trading_price(BTCtoUSDT_price['Bid'])) == 0:
      return 0
  else:
    profitUSDT = float()
    check_pointUSDT = 0
    profitUSDT = (workerBTC_Bid['Bid']*BTCtoUSDT_price['Bid'])/(USDTworker_Ask['Ask'])
    #print(profitUSDT)
    ### check the profit range ###
    if 1.015 <= profitUSDT:
      print(100*(profitUSDT-1), ' %')
      check_pointUSDT = 1
    else :
      pass

    return check_pointUSDT

def pricecheck_BTC (BTCworker_Ask, workerUSDT_Bid, USDTtoBTC_price):
  ### doubt ###
  if min(typecheck_trading_price(BTCworker_Ask['Ask']), typecheck_trading_price(workerUSDT_Bid['Bid']), typecheck_trading_price(USDTtoBTC_price['Ask'])) == 0:
      return 0
  else:
    profitBTC = float()
    check_pointBTC = 0
    profitBTC = workerUSDT_Bid['Bid']/(BTCworker_Ask['Ask']*USDTtoBTC_price['Ask'])
    #print(profitBTC)
    ### check the profit range ###
    if 1.015 <= profitBTC:
      print(100*(profitBTC-1), ' %')
      check_pointBTC = 1  
    else :
      pass

    return check_pointBTC

def cancel_order(market, coinname):
  ### cancel orders and return the states###
  order = check_order(market)
  if order == 'OrderUuidisGone':
    print('there is no order for ', coinname)
    pass
  else:
    my_bittrex1_1.cancel(order)
    print('cancel the order for', coinname)
    pass


def buycoin(market, quantity, tradingsignal, coinname, moneybuy):
  ### test not yet
  maincoin = market.split('-')
  my_bittrex1_1.buy_limit(market, quantity, tradingsignal)
  buyit = 1
  timeout=0
  if maincoin[0] == 'BTC':
    money = balance2_0.get_balance(maincoin[0])
    moneybuy = money['result']['Balance']
  else:
    pass

  ### start buying the coin ###
  while 1:
    balancebuy = balance2_0.get_balance(coinname)
    if check_none_balance(balancebuy) == 1:
      balancebuy = {}
      balancebuy['result'] = {}
      balancebuy['result']['Balance'] = 0.0
      pass
    else:
      pass

    if balancebuy['result']['Balance'] >= quantity:
      print('We buy it!!!')
      break

    else:
      if buyit == 12:
        ### cancel the order ###
        cancel_order(market, coinname)
        
        ###cancel (1) re-decide the quantity###
        tradingbuy = my_bittrex1_1.get_ticker(market)
        if check_tradingsignal(tradingbuy) == 0:###signal is exist
          quantity = quantity_decision(moneybuy, tradingbuy['result']['Ask'])
          buyprice = tradingbuy['result']['Ask']
          pass
        else:
          quantity = 0.99*quantity
          buyprice = tradingsignal
          pass

        if quantity*tradingsignal <0.0005:
          break
        else:
          pass
          
        ### cancel (2) wait toooooooo long time
        if timeout == 3 :
          break
        else: pass

        ###cancel (3) re-order
        my_bittrex1_1.buy_limit(market, quantity, buyprice)
        buyit = 0
        timeout+=1
        print('Buy again!!')
        
      else:
        buyit+=1
        pass

      time.sleep(1)

  if timeout == 3:
    return 0.0
  else:
    balancebuy = balance2_0.get_balance(coinname)
    return balancebuy['result']['Balance']

###notyet###
def USDTtoBTC(market, quantity, tradingsignal, moneychange):
  ### still thinking 
  my_bittrex1_1.buy_limit(market, quantity, tradingsignal)
  changeit = 1
  timeout = 0

  while 1:
    balancechange = balance2_0.get_balance('BTC')
    if check_none_balance(balancechange) == 1:
      balancechange = {}
      balancechange['result'] = {}
      balancechange['result']['Balance'] = 0.0
      pass
    else:
      pass

    if balancechange['result']['Balance'] >= quantity:
      print('We change from USDT to BTC!!! quantity = ', balancechange['result']['Balance'])
      break

    else:
      if changeit == 12:
        ### cancel the order ###
        cancel_order(market, 'BTC')

        ###cancel (1) re-decide the quantity###
        tradingchange = my_bittrex1_1.get_ticker(market)
        if check_tradingsignal(tradingchange) == 0:###signal is exist
          quantity = quantity_decision(moneychange, tradingchange['result']['Ask'])
          changeprice = tradingchange['result']['Ask']
          pass
        else:
          quantity = 0.99*quantity
          changeprice = tradingsignal
          pass

        if quantity*tradingsignal <0.0005:
          break
        else:
          pass

        ### cancel (2) wait toooooooo long time
        if timeout == 3 :
          break
        else: pass

        ###cancel (3) re-order
        my_bittrex1_1.buy_limit(market, quantity, changeprice)
        print('Buy again!!')
        changeit = 0
        timeout+=1
        
      else:
        changeit+=1
        pass

      time.sleep(1)

  ### timeout 
  if timeout == 3:
    return 0.0
  else:
    balancechange = balance2_0.get_balance('BTC')
    return balancechange['result']['Balance']

def sellcoin(market, quantity, tradingsignal, coinname):
  ###testing not yet
  my_bittrex1_1.sell_limit(market, quantity, tradingsignal)
  sellit = 1

  while 1:
    balancesell = balance2_0.get_balance(coinname)
    if check_none_balance(balancesell) == 1:
      print('still loading balance')
      continue
    else:
      pass

    if balancesell['result']['Balance'] <= 0.05*quantity :
      print('We sell it!!!')
      break

    else:
      if sellit == 12:
        ### cancel the order ###
        cancel_order(market, coinname)
        
        ###cancel (1) re-decide the quantity###
        tradingsell = my_bittrex1_1.get_ticker(market)
        if check_tradingsignal(tradingsell) == 0: ###signal is exist
          quantity = balancesell['result']['Balance']
          sellprice = tradingsell['result']['Bid']
          pass
        else:
          quantity = balancesell['result']['Balance']
          sellprice = tradingsignal
          pass

        if quantity*tradingsignal <0.0005:
          break
        else:
          pass
          
        ###cancel (2) re-order
        my_bittrex1_1.sell_limit(market, quantity, sellprice)
        sellit = 0
        print('Sell again!!')
      
      else:
        sellit+=1
        pass

    time.sleep(1)

def BTCtoUSDT(market, quantity, tradingsignal):
  my_bittrex1_1.sell_limit(market, quantity, tradingsignal)
  changeit = 1

  while 1:
    balancechange = balance2_0.get_balance('BTC')
    if check_none_balance(balancechange) == 1:
      print('still loading balance')
      continue
    else:
      pass

    if balancechange['result']['Balance'] <= 0.1*quantity :
      print('We sell it!!!')
      break

    else:
      if changeit == 12:
        ### cancel the order ###
        cancel_order(market, 'BTC')
        
        ###cancel (1) re-decide the quantity###
        tradingchange = my_bittrex1_1.get_ticker(market)
        if check_tradingsignal(tradingchange) == 0: ###signal is exist
          quantity = balancechange['result']['Balance']
          changeprice = tradingchange['result']['Bid']
          pass
        else:
          quantity = balancechange['result']['Balance']
          changeprice = tradingsignal
          pass

        if quantity*tradingsignal <0.0005:
          break
        else:
          pass
          
        ###cancel (2) re-order
        my_bittrex1_1.sell_limit(market, quantity, changeprice)
        changeit = 0
        print('Sell again!!')
      
      else:
        changeit+=1
        pass

    time.sleep(1)


### start the trading bot ###

####### read the data #######

#worker[i] = input("Please input the coin: ")
#total_worker = 2
#worker = ['BCC', 'NEO', 'ADA']
balance_USDT = balance2_0.get_balance('USDT')
balance_BTC = balance2_0.get_balance('BTC')
count = 1
countdown = 1
ordersleep = 0

### BTC_stability switch on/off ###
BTC_stab = str(input("Do you switch on BTC_stability mechanism? (on/off) : "))


### input worker ###
print()
print("Please input the running workers, and seperating with space " ".")
worker = str(input())
worker = worker.split(" ")
total_worker = len(worker) - 1
for j in range(0, len(worker), 1):
  time.sleep(2)
  balance_coin = balance2_0.get_balance(worker[j])
  if balance_coin['result'] is None:
    print(worker[j],": 0.0")
  else:
    print(worker[j],":  ", balance_coin['result']['Balance'])


##### show the balance #####

if balance_USDT['result'] is None:
  print("USDT : 0.0")
else :
  print("USDT : ", balance_USDT['result']['Balance'])

if balance_BTC['result'] is None:
  print("BTC : 0.0")
else :
  print("BTC :  ", balance_BTC['result']['Balance'])


### trading money & preparation ###
runmoney = int(input("Please input the running money(USDT in integer): "))
i = 0
record = 0
tstart = time.time()
BTCprice = my_bittrex1_1.get_ticker('USDT-BTC')['result']['Ask']
timecount = 0

### trading loop start ###

while 1:
  checknoneUSDT = 0
  checknoneBTC = 0
  checkUSDT_worker = 0
  checkBTC_worker = 0
  marketUSDT = 'USDT-' + worker[i]
  marketBTC = 'BTC-' + worker[i]

  BTC_price_now = my_bittrex1_1.get_ticker('USDT-BTC')
  USDT_worker_tradingsignal = my_bittrex1_1.get_ticker(marketUSDT)
  BTC_worker_tradingsignal = my_bittrex1_1.get_ticker(marketBTC)

  checknone = check_all_tradingsignal(USDT_worker_tradingsignal, BTC_worker_tradingsignal, BTC_price_now)
  
  if checknone == 0:

    if BTC_stab == 'on':
      BTCprice_stability(BTCprice, BTC_price_now)
      if BTCprice_stability == 1:
        x = str(datetime.datetime.now())
        x = x.split(".")
        print(str(x[0]))
        print("BTC_price is not stability now")
        print()
        BTC_price = BTC_price_now
        continue
      else:
        pass
    else: 
      pass

    #print(worker[i])
    checkUSDT_worker = pricecheck_USDT(USDT_worker_tradingsignal['result'], BTC_worker_tradingsignal['result'], BTC_price_now['result'])
    checkBTC_worker = pricecheck_BTC(BTC_worker_tradingsignal['result'], USDT_worker_tradingsignal['result'], BTC_price_now['result'])
    
    ### changing workers ###
    ### (OK) ###
    if checkUSDT_worker == 0:
      if checkBTC_worker == 0:
        i+=1
        if i > total_worker:
          i=0
        else:pass
        count+=1
      else: pass
    else: pass

    if checkUSDT_worker == 1:

      ### reading the USDT, buy the coin ###
      print("going to buy USDT -", worker[i])
      USDT_worker_tradingsignal1 = my_bittrex1_1.get_ticker(marketUSDT)

      if check_tradingsignal(USDT_worker_tradingsignal1) == 1:
        USDT_price = 1.001*USDT_worker_tradingsignal['result']['Ask']
      else:
        USDT_price = USDT_worker_tradingsignal1['result']['Ask']

      quantity_worker_pre = quantity_decision(runmoney, USDT_price)
      quantity_worker = buycoin(marketUSDT, quantity_worker_pre, USDT_price, worker[i], runmoney)
      print ("Buy the ", worker[i], ": ", quantity_worker, "at ", USDT_price)
      print()
      

      ### sell the coin ###
      BTC_worker_tradingsignal1 = my_bittrex1_1.get_ticker(marketBTC)
      if check_tradingsignal(BTC_worker_tradingsignal1) == 1:
        BTC_worker_price = BTC_worker_tradingsignal['result']['Bid']
      else:
        BTC_worker_price = BTC_worker_tradingsignal1['result']['Bid']

      print("Sell the ", worker[i], ":  ", quantity_worker, "at ", BTC_worker_price)
      print()
      sellcoin(marketBTC, quantity_worker, BTC_worker_price, worker[i])


      ### return to USDT ###
      balance_BTC = balance2_0.get_balance('BTC')
      BTC_price_now1 = my_bittrex1_1.get_ticker('USDT-BTC')
      if check_tradingsignal(BTC_price_now1) == 1:
        BTC_price = BTC_price_now['result']['Bid']
      else:
        BTC_price = BTC_price_now1['result']['Bid']

      print('return to USDT')
      BTCtoUSDT('USDT-BTC', balance_BTC['result']['Balance'], BTC_price)
      

      ### calculate the profit ###
      profit = ((balance_BTC['result']['Balance']) * (BTC_price)) - quantity_worker_pre*USDT_price
      print(profit, ' USDT')
      if (profit/runmoney) <= 0.5:
        runmoney += profit
      else:
        pass
      checkUSDT_worker = 0
      quantity_worker = 0.0



    elif checkBTC_worker == 1:
      ### buy BTC ###
      print("going to buy BTC-", worker[i])
      BTC_price_now1 = my_bittrex1_1.get_ticker('USDT-BTC')

      if check_tradingsignal(BTC_price_now1) == 1:
        BTC_price = BTC_price_now['result']['Ask']
      else:
        BTC_price = BTC_price_now1['result']['Ask']
      
      quantity_BTC = quantity_decision(runmoney, BTC_price)
      print('Buy the BTC ', quantity_BTC, "at ", BTC_price)
      print()
      quantity_BTC = USDTtoBTC('USDT-BTC', quantity_BTC, BTC_price, runmoney)


      ### buy the coin
      BTC_worker_tradingsignal1 = my_bittrex1_1.get_ticker(marketBTC)
      if check_tradingsignal(BTC_worker_tradingsignal1) == 1:
        BTC_worker_price = BTC_worker_tradingsignal['result']['Ask']
      else:
        BTC_worker_price = BTC_worker_tradingsignal1['result']['Ask']


      quantity_worker = quantity_decision(quantity_BTC, BTC_worker_price)
      print("Buy the ", worker[i],":  ", quantity_worker, " at ", BTC_worker_price)
      print()
      quantity_worker = buycoin(marketBTC, quantity_worker, BTC_worker_price, worker[i], quantity_BTC)

      if quantity_worker == 0.0:
        print("Sorry, return to USDT")
        BTCtoUSDT('USDT-BTC', quantity_BTC, BTC_worker_price)
        runmoney = runmoney + quantity_BTC*((0.9975*BTC_worker_tradingsignal['result']['Bid'])-(1.0025*BTC_worker_tradingsignal['result']['Ask']))
        ordersleep = 1
        pass
      else:
        pass


      ### sell the coin from USDT-worker[i] ###
      USDT_worker_tradingsignal1 = my_bittrex1_1.get_ticker(marketUSDT)
      if check_tradingsignal(USDT_worker_tradingsignal1) == 1:
        USDT_price = USDT_worker_tradingsignal['result']['Bid']
      else:
        USDT_price = USDT_worker_tradingsignal1['result']['Bid']

      print("Sell the ", worker[i],":  ", quantity_worker)
      print()
      sellcoin(marketUSDT, quantity_worker, USDT_price, worker[i])


      ### calculate the profit ###

      profit = quantity_worker*USDT_price - quantity_BTC*BTC_price
      print(profit, ' USDT')
      if (profit/runmoney) <= 0.5:
        runmoney += profit
      else:
        pass
      
      checkBTC_worker = 0 
      quantity_worker = 0.0
    
    else :
      count +=1

      if count % 100 == 0:
        BTC_price = BTC_price_now
      
      elif count % 1000 == 0:
        count = 1
        countdown +=1
        time.sleep(10)
        balance_USDT = balance2_0.get_balance('USDT')
        runmoney = math.floor(balance_USDT['result']['Balance'])
        print("runmoney is ", runmoney)
        #BTC_price_pre = my_bittrex1_1.get_ticker('USDT-BTC')
        pass

      elif countdown % 2 ==0:
        countdown = 1
        print()
        x = str(datetime.datetime.now())
        x = x.split('.')
        print(str(x[0]))
        print('still waiting')
        print()

      else:
        continue


    balance_USDT = balance2_0.get_balance('USDT')
    if balance_USDT['result'] is None:
      pass
    else :
      runmoney = math.floor(balance_USDT['result']['Balance'])

  else:
    y = str(datetime.datetime.now())
    y = y.split(".")
    print(str(y[0]))
    print(worker[i], 'has some problem!!')
    pass

  if ordersleep == 1:
    time.sleep(300)
    ordersleep = 0
    pass
  else:
    pass

  ### calculating the programming time ###
  tend = time.time()
  timecount+=1
  if timecount == 999:
    delta = tend - tstart
    print("the delta time is ", delta, " (1000)")
    print()
    timecount == 0


     
