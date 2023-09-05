from typing import Optional

from numba import int64, boolean, float64

from ..order import LIMIT, BUY, SELL
from ..reader import WAIT_ORDER_RESPONSE_NONE, COL_LOCAL_TIMESTAMP, UNTIL_END_OF_DATA


class MultiAssetHftBacktest:
    r"""
    Multi Asset HftBacktest.

    .. warning::
        This has to be constructed by :func:`.HftBacktest`.

    Args:
        locals: Local processors.
        exchs: Exchange processors.
    """

    def __init__(self, locals, exchs):
        self.locals = locals
        self.exchs = exchs

        #: Whether a backtest has finished.
        self.run = True

        timestamp = UNTIL_END_OF_DATA
        for local in self.locals:
            timestamp = min(timestamp, local.next_data[0, COL_LOCAL_TIMESTAMP])

        #: Current timestamp
        self.current_timestamp = timestamp

    def position(self, asset: int64):
        """
        Current position.
        """
        return self.locals[asset].state.position

    def balance(self, asset: Optional[int64]):
        """
        Current balance..
        """
        if asset is None:
            balance = 0
            for local in self.locals:
                balance += local[asset].state.balance
            return balance
        else:
            return self.locals[asset].state.balance

    def fee(self, asset: Optional[int64]):
        if asset is None:
            fee = 0
            for local in self.locals:
                fee += local[asset].state.fee
            return fee
        else:
            return self.locals[asset].state.fee

    def trade_num(self, asset: int64):
        return self.locals[asset].state.trade_num

    def trade_qty(self, asset: int64):
        return self.locals[asset].state.trade_qty

    def trade_amount(self, asset: int64):
        return self.locals[asset].state.trade_amount

    def orders(self, asset: int64):
        """
        Orders dictionary.
        """
        return self.locals[asset].orders

    def tick_size(self, asset: int64):
        """
        Tick size
        """
        return self.locals[asset].depth.tick_size

    def high_ask_tick(self, asset: int64):
        """
        The highest ask price in the market depth in tick.
        """
        return self.locals[asset].depth.high_ask_tick

    def low_bid_tick(self, asset: int64):
        """
        The lowest bid price in the market depth in tick.
        """
        return self.locals[asset].depth.low_bid_tick

    def best_bid_tick(self, asset: int64):
        """
        The best bid price in tick.
        """
        return self.locals[asset].depth.best_bid_tick

    def best_ask_tick(self, asset: int64):
        """
        The best ask price in tick.
        """
        return self.locals[asset].depth.best_ask_tick

    def best_bid(self, asset: int64):
        """
        The best bid price.
        """
        return self.best_bid_tick(asset) * self.tick_size(asset)

    def best_ask(self, asset: int64):
        """
        The best ask price.
        """
        return self.best_ask_tick(asset) * self.tick_size(asset)

    def bid_depth(self, asset: int64):
        """
        Bid market depth.
        """
        return self.locals[asset].depth.bid_depth

    def ask_depth(self, asset: int64):
        """
        Ask market depth.
        """
        return self.locals[asset].depth.ask_depth

    def mid(self, asset: int64):
        """
        Mid-price of BBO.
        """
        return (self.best_bid(asset) + self.best_ask(asset)) / 2.0

    def equity(self, asset: Optional[int64]):
        """
        Current equity value.
        """
        if asset is None:
            equity = 0
            for asset, local in enumerate(self.locals):
                equity += local.state.equity(self.mid(asset))
            return equity
        else:
            return self.locals[asset].state.equity(self.mid(asset))

    def last_trade(self, asset: int64):
        """
        Last market trade. If ``None``, no last market trade.
        """
        if self.locals[asset].trade_len > 0:
            return self.last_trades(asset)[self.locals[asset].trade_len - 1]
        else:
            return None

    def last_trades(self, asset: int64):
        """
        An array of last market trades.
        """
        return self.locals[asset].last_trades[:self.locals[asset].trade_len]

    @property
    def local_timestamp(self):
        return self.current_timestamp

    def submit_buy_order(
            self,
            asset: int64,
            order_id: int64,
            price: float64,
            qty: float64,
            time_in_force: int64,
            order_type: int64 = LIMIT,
            wait: boolean = False
    ):
        r"""
        Places a buy order.

        Args:
            asset:
            order_id: The unique order ID; there should not be any existing order with the same ID on both local and
                      exchange sides.
            price: Order price.
            qty: Quantity to buy.
            time_in_force: Available Time-In-Force options vary depending on the exchange model. See to the exchange
                           model for details.

                           - ``GTX``: Post-only
                           - ``GTC``: Good 'till Cancel
                           - ``FOK``: Fill or Kill
                           - ``IOC``: Immediate or Cancel
            order_type: Currently, only ``LIMIT`` is supported. To simulate a ``MARKET`` order, set the price very high.
            wait: If ``True``, wait until the order placement response is received.

        Returns:
            ``True`` if the method reaches the specified timestamp within the data. If the end of the data is reached
            before the specified timestamp, it returns ``False``.
        """
        self.locals[asset].submit_order(order_id, BUY, price, qty, order_type, time_in_force, self.current_timestamp)

        if wait:
            return self.goto(UNTIL_END_OF_DATA, asset=asset, wait_order_response=order_id)
        return True

    def submit_sell_order(
            self,
            asset: int64,
            order_id: int64,
            price: float64,
            qty: float64,
            time_in_force: int64,
            order_type: int64 = LIMIT,
            wait: boolean = False
    ):
        r"""
        Places a sell order.

        Args:
            asset:
            order_id: The unique order ID; there should not be any existing order with the same ID on both local and
                      exchange sides.
            price: Order price.
            qty: Quantity to sell.
            time_in_force: Available Time-In-Force options vary depending on the exchange model. See to the exchange
                           model for details.

                           - ``GTX``: Post-only
                           - ``GTC``: Good 'till Cancel
                           - ``FOK``: Fill or Kill
                           - ``IOC``: Immediate or Cancel
            order_type: Currently, only ``LIMIT`` is supported. To simulate a ``MARKET`` order, set the price very low.
            wait: If ``True``, wait until the order placement response is received.

        Returns:
            ``True`` if the method reaches the specified timestamp within the data. If the end of the data is reached
            before the specified timestamp, it returns ``False``.
        """
        self.locals[asset].submit_order(order_id, SELL, price, qty, order_type, time_in_force, self.current_timestamp)

        if wait:
            return self.goto(UNTIL_END_OF_DATA, asset=asset, wait_order_response=order_id)
        return True

    def cancel(self, asset: int64, order_id: int64, wait: boolean = False):
        r"""
        Cancel the specified order.

        Args:
            asset:
            order_id: Order ID to cancel.
            wait: If ``True``, wait until the order placement response is received.

        Returns:
            ``True`` if the method reaches the specified timestamp within the data. If the end of the data is reached
            before the specified timestamp, it returns ``False``.
        """
        self.locals[asset].cancel(order_id, self.current_timestamp)

        if wait:
            return self.goto(UNTIL_END_OF_DATA, asset=asset, wait_order_response=order_id)
        return True

    def wait_order_response(self, asset: int64, order_id: int64, timeout: int64 = -1):
        r"""
        Wait for the specified order response by order ID.

        Args:
            asset:
            order_id: The order ID to wait for.
            timeout: Maximum waiting time; The default value of `-1` indicates no timeout.

        Returns:
            ``True`` if the method reaches the specified timestamp within the data. If the end of the data is reached
            before the specified timestamp, it returns ``False``.
        """
        if self.locals[asset].orders_from.__contains__(order_id):
            timestamp = self.locals[asset].orders_from.get(order_id)
            return self.goto(timestamp)

        if not self.locals[asset].orders_to.__contains__(order_id):
            return True

        if timeout >= 0:
            timestamp = self.current_timestamp + timeout
        else:
            timestamp = UNTIL_END_OF_DATA

        return self.goto(timestamp, asset=asset, wait_order_response=order_id)

    def clear_inactive_orders(self, asset: Optional[int64] = None):
        r"""
        Clear inactive(``CANCELED``, ``FILLED``, or ``EXPIRED``) orders from the local ``orders`` dictionary.

        Args:
            asset:
        """
        if asset is None:
            for local in self.locals:
                local.clear_inactive_orders()
        else:
            self.locals[asset].clear_inactive_orders()

    def clear_last_trades(self, asset: Optional[int64] = None):
        r"""
        Clears the last trades(market trades) from the buffer.

        Args:
            asset:
        """
        if asset is None:
            for local in self.locals:
                local.clear_last_trades()
        else:
            self.locals[asset].clear_last_trades()

    def get_user_data(self, asset: int64, event: int64):
        r"""
        Retrieve custom user event data.

        Args:
            asset:
            event: Event identifier. Refer to the data documentation for details on incorporating custom user data with
                   the market feed data.

        Returns:
            The latest event data for the specified event.
        """
        return self.locals[asset].get_user_data(event)

    def elapse(self, duration: float64):
        r"""
        Elapses the specified duration.

        Args:
            duration: Duration to elapse. Unit should be the same as the feed data's timestamp unit.

        Returns:
            ``True`` if the method reaches the specified timestamp within the data. If the end of the data is reached
            before the specified timestamp, it returns ``False``.
        """
        return self.goto(self.current_timestamp + duration)

    def goto(
            self,
            timestamp: float64,
            # asset: Optional[int64] = None,
            wait_order_response: int64 = WAIT_ORDER_RESPONSE_NONE
    ):
        r"""
        Goes to a specified timestamp.

        This method moves to the specified timestamp, updating the backtesting state to match the corresponding time. If
        ``wait_order_response`` is provided, the method will stop and return when it receives the response for the
        specified order.

        Args:
            timestamp: The target timestamp to go to. The timestamp unit should be the same as the feed data's timestamp
                       unit.
            asset:
            wait_order_response: Order ID to wait for; the default value is ``WAIT_ORDER_RESPONSE_NONE``, which means
                                 not waiting for any order response.

        Returns:
            ``True`` if the method reaches the specified timestamp within the data. If the end of the data is reached
            before the specified timestamp, it returns ``False``.
        """
        found_order_resp_timestamp = False
        while True:
            # Select which side will be processed next.
            next_local_timestamp = -1
            next_local_proc = self.locals[0] # to type assign
            for local in self.locals:
                timestamp = local.next_timestamp()
                if timestamp >= 0 or next_local_timestamp == -1:
                    if timestamp < next_local_timestamp:
                        next_local_timestamp = timestamp
                        next_local_proc = local

            next_exch_timestamp = -1
            next_exch_proc = self.exchs[0] # to type assign
            next_exch_index = -1
            for i, exch in enumerate(self.exchs):
                timestamp = exch.next_timestamp()
                if timestamp > 0 or next_exch_timestamp == -1:
                    if timestamp < next_exch_timestamp:
                        next_exch_timestamp = timestamp
                        next_exch_proc = exch
                        next_exch_index = i

            # Local will be processed.
            if (0 < next_local_timestamp < next_exch_timestamp) \
                    or (next_local_timestamp > 0 >= next_exch_timestamp):
                if next_local_timestamp > timestamp:
                    break
                resp_timestamp = next_local_proc.process(WAIT_ORDER_RESPONSE_NONE)

            # Exchange will be processed.
            elif (0 < next_exch_timestamp <= next_local_timestamp) \
                    or (next_exch_timestamp > 0 >= next_local_timestamp):
                if next_exch_timestamp > timestamp:
                    break
                # if asset is not None and next_exch_index == asset:
                #     resp_timestamp = next_exch_proc(
                #         wait_order_response if not found_order_resp_timestamp else WAIT_ORDER_RESPONSE_NONE
                #     )
                # else:
                resp_timestamp = next_exch_proc(WAIT_ORDER_RESPONSE_NONE)

            # No more data or orders to be processed.
            else:
                self.run = False
                break

            if resp_timestamp > 0:
                found_order_resp_timestamp = True
                timestamp = resp_timestamp

        self.current_timestamp = timestamp

        if not self.run:
            return False
        return True
