import asyncio, os, multiprocessing
from queue import Queue
from threading import Thread
from LiveTradingConfig import *
import SharedHelper
from Helper import *
from TradeManager import *

if __name__ == '__main__':
    log.info(f'Configuration:\nstrategy: {trading_strategy}\nleverage: {leverage}\norder-size: {order_size}\ninterval: {interval}\nTP/SL choice: {TP_SL_choice}\nSL mult: {SL_mult}\nTP mult: {TP_mult}\ntrade all symbols: {trade_all_symbols}\nsymbols to trade: {symbols_to_trade}\nuse trailing stop: {use_trailing_stop}\ntrailing stop callback: {trailing_stop_callback}\ntrading threshold: {trading_threshold}\nuse market orders: {use_market_orders}\nmax number of positions: {max_number_of_positions}\nuse multiprocessing for trade execution: {use_multiprocessing_for_trade_execution}\ncustom TP/SL Functions: {custom_tp_sl_functions}\nmake decision options: {make_decision_options}\n')
    if os.name == 'nt': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    Q = multiprocessing.Queue if use_multiprocessing_for_trade_execution else Queue
    signal_queue, print_trades_q = Q(), Q()
    python_binance_client = Client(api_key=API_KEY, api_secret=API_SECRET)
    client = CustomClient(python_binance_client)
    if trade_all_symbols: symbols_to_trade = SharedHelper.get_all_symbols(python_binance_client, coin_exclusion_list)
    client.set_leverage(symbols_to_trade)
    Bots = []
    client.setup_bots(Bots, symbols_to_trade, signal_queue, print_trades_q)
    client.start_websockets(Bots)
    if use_multiprocessing_for_trade_execution:
        new_trade_loop = multiprocessing.Process(target=start_new_trades_loop_multiprocess, args=(python_binance_client, signal_queue, print_trades_q))
        new_trade_loop.start()
    else:
        TM = TradeManager(python_binance_client, signal_queue, print_trades_q)
        new_trade_loop = Thread(target=TM.new_trades_loop, daemon=True)
        new_trade_loop.start()
    Thread(target=client.ping_server_reconnect_sockets, args=(Bots,), daemon=True).start()
    if auto_calculate_buffer:
        buffer = convert_buffer_to_string(SharedHelper.get_required_buffer(trading_strategy))
    Thread(target=client.combine_data, args=(Bots, symbols_to_trade, buffer), daemon=True).start()
    new_trade_loop.join()
