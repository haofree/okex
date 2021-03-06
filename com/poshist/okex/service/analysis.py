from com.poshist.okex.service.notice import notice
from com.poshist.okex.service.rule import rule

from com.poshist.okex.service.util import jsonLoad


def analysisWsMessage(type,message,ws):

    if'['==message[0:1]:
        jm=jsonLoad(message[1:len(message)-1])
        # print(jm)
        if(None==jm.get('channel')):

            if ('depth'==jm.get('type')):
                analysisOrder(type, jm,ws)
            elif('deal'==jm.get('type')):
                analysisDeal(type,jm,ws)
            elif('kline'==jm.get('type')):
                print(jm)
                analysisKline(type,jm,ws)

def analysisKline(type,jm,ws):
    klines=jm.get('data')
    if len(klines)==1:
        kline=klines[0]
        if  ws.info[1]==0:
            if float(kline['volume'])>0:
                str1='无限大'
                notice(type, 'klineVule', [kline['volume'], kline['createdDate'], str1])
        else:
            if float(kline['volume'])/ws.info[1]>=rule.klineValue :
                str1=str(float(kline['volume'])/ws.info[1]*100)+'%'
                notice(type,'klineVule',[kline['volume'],kline['createdDate'],str1])

    for kline in klines:
        ws.info[1]=float(kline['volume'])


def analysisOrder(type,jm,ws):
    sellOrders=jm.get('data').get('asks')
    buyOrders=jm.get('data').get('bids')

    for sellorder in sellOrders:
        #大额卖单挂单判断
        if float(sellorder['price'])>ws.info[0]*(1-rule.orderChange) and float(sellorder['price'])<ws.info[0]*(1+rule.orderChange):

            if float(sellorder['totalSize'])>=rule.sellOrder:
                if (None==ws.sellOrders.get(sellorder['price'])):
                    notice(type, 'sellOrder', [sellorder['price'], sellorder['totalSize']])
                else:
                    if float(sellorder['totalSize'])-ws.sellOrders.get(sellorder['price'])>=rule.sellOrder:
                        notice(type,'sellOrder',[sellorder['price'],float(sellorder['totalSize'])-ws.sellOrders.get(sellorder['price'])])
            #大额卖单撤单判断
            if(None!=ws.sellOrders.get(sellorder['price'])):
                if ws.sellOrders.get(sellorder['price'])-float(sellorder['totalSize'])>=rule.sellOrder:
                    notice(type, 'sellOrderLost', [sellorder['price'], str(ws.sellOrders.get(sellorder['price'])-float(sellorder['totalSize']))])
        ws.sellOrders[sellorder['price']]=float(sellorder['totalSize'])

    for buyOrder in buyOrders:
        if float(buyOrder['price']) > ws.info[0] * (1 - rule.orderChange) and float(buyOrder['price']) < ws.info[ 0] * (1 + rule.orderChange):
        #大额买单挂单预警
            if float(buyOrder['totalSize'])>=rule.buyOrder:
                if (None == ws.buyOrders.get(buyOrder['price'])):
                    notice(type,'buyOrder',[buyOrder['price'],buyOrder['totalSize']])
                else :
                    if float(buyOrder['totalSize'])-ws.buyOrders.get(sellorder['price'])>=rule.sellOrder:
                        notice(type, 'buyOrder', [buyOrder['price'], float(buyOrder['totalSize'])-ws.buyOrders.get(sellorder['price'])])

            #大额买单撤单预警
            if(None!=ws.buyOrders.get(buyOrder['price'])):
                if ws.buyOrders.get(buyOrder['price'])-float(buyOrder['totalSize'])>=rule.buyOrder:
                    notice(type, 'buyOrderLost', [buyOrder['price'], str(ws.buyOrders.get(buyOrder['price'])-float(buyOrder['totalSize']))])
        ws.buyOrders[buyOrder['price']]=float(buyOrder['totalSize'])

def analysisDeal(type,jm,ws):

    deals=jm.get('data')
    for deal in deals:
        #大额交易判断
        if float(deal.get('amount'))>=rule.deal:
            notice(type,'deal',[deal.get('amount'),deal.get('price'),deal.get('createdDate'),deal.get('side')])
            if 0 == ws.info[2]:
                 ws.info[2]=deal.get('createdDate')
            else :
                if (int(deal.get('createdDate'))-ws.info[2])/1000>rule.dealbeetwn:
                    notice(type, 'dealbeetwn', deal.get('createdDate'))
        #交易差值判断
        if ws.dealInit:
            ws.dealInit=False
        else:
            change=(float(deal.get('price'))-ws.info[0])/ws.info[0]
            change1=change
            if change<0:
                change1=0-change
            if change1>rule.dealChange:
               notice(type,'dealChange',[deal.get('amount'),deal.get('price'),deal.get('createdDate'),change*100])
        ws.info[0] = float(deal.get('price'))
        if None!=ws.sellOrders.get(deal.get('price')):
            ws.sellOrders[deal.get('price')]=ws.sellOrders.get(deal.get('price'))-float(deal.get('amount'))
        if None!=ws.buyOrders.get(deal.get('price')):
            ws.buyOrders[deal.get('price')]=ws.buyOrders.get(deal.get('price'))-float(deal.get('amount'))




