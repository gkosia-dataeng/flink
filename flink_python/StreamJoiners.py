import logging
from pyflink.datastream.functions import BroadcastProcessFunction, CoProcessFunction
from pyflink.datastream.state import MapStateDescriptor
from pyflink.common.typeinfo import Types


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




union_brdcst_messages_state_descr = MapStateDescriptor("union_brdcst_messages", Types.STRING(), Types.TUPLE([Types.LONG(),Types.LONG(),Types.LONG(), Types.STRING(), Types.LONG(), Types.STRING(), Types.STRING()]))
order_details_descr = MapStateDescriptor("orders_details",   Types.LONG(), Types.TUPLE([Types.LONG(), Types.STRING()]) )
orders_enriched_descr =MapStateDescriptor("orders_enriched", Types.LONG(), Types.TUPLE([Types.LONG(), Types.STRING(), Types.LONG(), Types.STRING()]) )


class BroadcastEnrichmentInfo(BroadcastProcessFunction):

    def __init__(self, union_brdcst_messages_state_descr):
        self.union_brdcst_messages_state_descr = union_brdcst_messages_state_descr

    # trader or symbol or trader group
    def process_broadcast_element(self, data, ctx):
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
                 data['trader_id']
                ,data['login']
                ,data['trader_group_id']
                ,data['trader_group_name']
                ,data['symbol_id']
                ,data['symbol_name']
                ,data['src']
            )

            state.put(key, state_value)
            logger.info(f"process_broadcast_element: stored broadcasted object in state with key {key}")


    def process_element(self, position, ctx):
        
        logger.info(f"process_element: {str(position)}")
        symbol_id = "s_" + str(position[1])
        trader_id = "t_" + str(position[2])
        

        enriched_position = {
                    "position_id": position['position_id']
        }


        state = ctx.get_broadcast_state(self.union_brdcst_messages_state_descr)

        # enrich from symbol
        symbol = state.get(symbol_id)
        trader = state.get(trader_id)


        if symbol and trader:
            enriched_position["symbol"] = symbol[5]
            enriched_position["login"] = trader[1]

            logger.info(f"process_element: Successfully enriched position {enriched_position}")
            return [enriched_position]
        else:
            logger.info(f"process_element: Missing enrichment info for position {enriched_position}")
                
        
        

class PositionsOrdersJoin(CoProcessFunction):

    def open(self, runtime_context):
        self.orders_state = runtime_context.get_map_state(order_details_descr)

    def process_element1(self, position, ctx):
        order_info = self.orders_state.get(position['position_id'])
        position['order_id'] = order_info[0]
        position['type'] = order_info[1]


        logger.info(f"process_element1 - PositionsOrdersJoin : Position match with order: {position}")
        return [position]

    def process_element2(self, order, ctx):
        self.orders_state.put(order['position_id'], (order['order_id'], order['type'],))
        logger.info(f"process_element2 - PositionsOrdersJoin : Order stored in state: {order}")





class OrdersDealsJoin(CoProcessFunction):
    
    def open(self, runtime_context):
        self.orders_state = runtime_context.get_map_state(orders_enriched_descr)

    def process_element1(self, deal, ctx):
        order = self.orders_state.get(deal['order_id'])


        if order:
            position_id = order[0]
            symbol = order[1]
            login = order[2]
            type = order[3]

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

            logger.info(f"process_element1 -  OrdersDealsJoin: Deal enriched {msg}")
            return [msg]
        else:
            logger.info(f"process_element1 -  OrdersDealsJoin: Order info not found for deal {deal['deal_id']}")


    def process_element2(self, order, ctx):
        logger.info(f"process_element2 -  OrdersDealsJoin: Enriched Order stored in state {order}")
        self.orders_state.put(order['order_id'], (order['position_id'], order['symbol'],order['login'], order['type']))
