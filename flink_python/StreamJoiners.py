import logging
from pyflink.datastream.functions import BroadcastProcessFunction, CoProcessFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.common.typeinfo import Types


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




union_brdcst_messages_state_descr = MapStateDescriptor("union_brdcst_messages", Types.STRING(), Types.TUPLE([Types.LONG(),Types.LONG(),Types.LONG(), Types.STRING(), Types.LONG(), Types.STRING(), Types.STRING()]))
order_details_descr = MapStateDescriptor("orders_details", Types.LONG(), Types.TUPLE([Types.LONG(), Types.STRING()]) )
orders_enriched_descr =MapStateDescriptor("orders_enriched", Types.LONG(), Types.TUPLE([Types.LONG(), Types.STRING(), Types.LONG(), Types.STRING()]) )

class BroadcastEnrichmentInfo(BroadcastProcessFunction):

    def __init__(self, union_brdcst_messages_state_descr):
        self.union_brdcst_messages_state_descr = union_brdcst_messages_state_descr

        
    def process_broadcast_element(self, value, ctx):
        data = value
        logger.info(f"process_broadcast_element: {data}")

        state = ctx.get_broadcast_state(self.union_brdcst_messages_state_descr)

        if data['src'] == 'trader':
            key =  "t_" + str(data['trader_id'])
        elif data['src'] == 'trader_group':
            key =  "tg_" + str(data['trader_group_id'])
        elif data['src'] == 'symbol':
            key =  "s_" + str(data['symbol_id'])
        else:
            key = None
            logger.info(f"process_broadcast_element: Received {data} but not matched with a type")

        if key:
            state_value  = (
                 data['trader_id'] if data['trader_id'] is not None else -99
                ,data['login']  if data['login'] is not None else -99
                ,data['trader_group_id']  if data['trader_group_id'] is not None else -99
                ,data['trader_group_name']  if data['trader_group_name'] is not None else ""
                ,data['symbol_id']  if data['symbol_id'] is not None else -99
                ,data['symbol_name']  if data['symbol_name'] is not None else ""
                ,data['src']
            )

            state.put(key, state_value)
            logger.info(f"zzzz process_broadcast_element: stored in state element key: {key}, value {state_value}")
            troubleshoot = state.get(key)
            logger.info(f"zzzz process_broadcast_element: got from state after put: {troubleshoot}")

        for key in state.keys():
            logger.info(f"zzzz process_broadcast_element: State keys {key}")



    def process_element(self, value, ctx):
        position = value
        logger.info(f"zzzz process_element: {str(position)}")
        symbol_id = "s_" + str(position[1])
        trader_id = "t_" + str(position[2])


        logger.info(f"zzzz process_element symbol_id: {symbol_id}, trader_id: {trader_id}")
        
        state = ctx.get_broadcast_state(self.union_brdcst_messages_state_descr)
        
        for key in state.keys():  
            stored_value = state.get(key)  
            print(f"zzzz process_element: Key: {key}, Value: {stored_value}")
        
        symbol = state.get(symbol_id)

        logger.info(f"zzzz process_element symbol readed from state {symbol}")


        enriched_position = {
                 'position_id': position['position_id']
                }
        
        if symbol:
            
            enriched_position['symbol'] = symbol[5]
            trader = state.get(trader_id)

            if trader:
                enriched_position['login'] = trader[1]
            else:
                logger.info(f"zzzz process_element Didnt find trader, trader key {trader_id}")
                for key in state.keys():  
                    stored_value = state.get(key)  
                    print(f"zzzz process_element: Didnt find trader, Key: {key}, Value: {stored_value}")

        
        
        return [enriched_position]
    


class PositionsOrdersJoin(CoProcessFunction):

    def open(self, runtime_context):
        self.orders_state = runtime_context.get_map_state(order_details_descr)

    def process_element1(self, position, ctx):
        order_info = self.orders_state.get(position['position_id'])
        position['order_id'] = order_info[0]
        position['type'] = order_info[1]

        return [position]

    def process_element2(self, order, ctx):
        self.orders_state.put(order['position_id'], (order['order_id'], order['type'],))





class OrdersDealsJoin(CoProcessFunction):
    
    def open(self, runtime_context):
        self.orders_state = runtime_context.get_map_state(orders_enriched_descr)

    def process_element1(self, deal, ctx):
        order_info = self.orders_state.get(deal['order_id'])


        if order_info:
            position_id = order_info[0]
            symbol = order_info[1]
            login = order_info[2]
            type = order_info[3]

            msg = {
                 "deal_id": deal['deal_id']
                ,"order_id": deal['order_id']
                ,"position_id": position_id
                ,"symbol": symbol
                ,"login": login
                ,"type": type
                ,"profit": deal['profit']
                ,"create_date": deal['create_date']
                ,"update_time": deal['update_time']
            }

            logger.info(f"zzzz processed_deal {msg}")
            return [msg]
        else:
            logger.info(f"zzzz processed_deal for deal {deal}")
            logger.info(f"zzzz processed_deal order info not found for deal {deal['deal_id']}")


    def process_element2(self, order, ctx):
        logger.info(f"zzzz processed_deal received order enriched {order}")
        self.orders_state.put(order['order_id'], (order['position_id'], order['symbol'],order['login'], order['type']))

        for key in self.orders_state.keys():
            logger.info(f"zzzz processed_deal current key in orders enriched {key}")
