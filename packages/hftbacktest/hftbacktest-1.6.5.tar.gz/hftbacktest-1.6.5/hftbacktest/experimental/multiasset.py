from typing import List, Optional, Callable

import numpy as np
import pandas as pd
from numba import boolean, int64, typeof
from numba.experimental import jitclass
from numba.typed import List

from .backtest import MultiAssetHftBacktest as MultiAssetHftBacktest_
from .. import __load_data, RiskAverseQueueModel
from ..marketdepth import MarketDepth
from ..order import OrderBus
from ..proc.local import LocalInit
from ..proc.nopartialfillexchange import NoPartialFillExchange, NoPartialFillExchangeInit
from ..reader import (
    DataReader,
    Cache
)
from ..state import StateInit
from ..typing import (
    Data,
    ExchangeModelInitiator,
    AssetType,
    OrderLatencyModel,
    DataCollection, QueueModel
)


# JIT'ed HftBacktest
def MultiAssetHftBacktest(locals, exchs):
    jitted = jitclass(spec=[
        ('run', boolean),
        ('current_timestamp', int64),
        ('locals', typeof(locals)),
        ('exchs', typeof(exchs)),
    ])(MultiAssetHftBacktest_)
    return jitted(locals, exchs)


class Asset:
    data: DataCollection
    tick_size: float
    lot_size: float
    maker_fee: float
    taker_fee: float
    snapshot: Optional[Data]
    start_position: float
    start_balance: float
    start_fee: float

    def __init__(
            self,
            data: DataCollection,
            tick_size: float,
            lot_size: float,
            maker_fee: float,
            taker_fee: float,
            snapshot: Optional[Data]
    ):
        self.data = data
        self.tick_size = tick_size
        self.lot_size = lot_size
        self.maker_fee = maker_fee
        self.taker_fee = taker_fee
        self.snapshot = snapshot
        self.start_position = 0
        self.start_balance = 0
        self.start_fee = 0


def HftBacktest(
        assets: List[Asset],
        order_latency: Callable[[], OrderLatencyModel],
        asset_type: Callable[[], AssetType],
        queue_model: Optional[Callable[[], QueueModel]] = None,
        trade_list_size: int = 0,
        exchange_model: Optional[ExchangeModelInitiator] = None
):
    r"""
    Create a HftBacktest instance.

    Args:
        data: Data to be fed.
        tick_size: Minimum price increment for the given asset.
        lot_size: Minimum order quantity for the given asset.
        maker_fee: Maker fee rate; a negative value indicates rebates.
        taker_fee: Taker fee rate; a negative value indicates rebates.
        order_latency: Order latency model. See :doc:`Order Latency Models <order_latency_models>`.
        asset_type: Either ``Linear`` or ``Inverse``. See :doc:`Asset types <asset_types>`.
        queue_model: Queue model with default set as :class:`.models.queue.RiskAverseQueueModel`. See :doc:`Queue Models <queue_models>`.
        snapshot: The initial market depth snapshot.
        start_position: Starting position.
        start_balance: Starting balance.
        start_fee: Starting cumulative fees.
        trade_list_size: Buffer size for storing market trades; the default value of ``0`` indicates that market trades
                         will not be stored in the buffer.
        exchange_model: Exchange model with default set as ``NoPartialFillExchange``.

    Returns:
         JIT'ed :class:`.SingleAssetHftBacktest`
    """
    if queue_model is None:
        queue_model = RiskAverseQueueModel

    if exchange_model is None:
        exchange_model = NoPartialFillExchange

    locals = None
    exchs = None

    local_reader = DataReader(Cache())
    state_init = StateInit(asset_type())
    sample_state = state_init(
            0,
            0,
            0,
            0,
            0,
            asset_type()
        )
    local_init = LocalInit(local_reader, sample_state, order_latency())
    exch_init = NoPartialFillExchangeInit(
            local_reader,
            sample_state,
            order_latency(),
            queue_model()
        )

    for asset in assets:
        cache = Cache()

        if isinstance(asset.data, list):
            local_reader = DataReader(cache)
            exch_reader = DataReader(cache)
            for item in asset.data:
                if isinstance(item, str):
                    local_reader.add_file(item)
                    exch_reader.add_file(item)
                elif isinstance(item, pd.DataFrame) or isinstance(item, np.ndarray):
                    local_reader.add_data(item)
                    exch_reader.add_data(item)
                else:
                    raise ValueError('Unsupported data type')
        elif isinstance(asset.data, str):
            local_reader = DataReader(cache)
            local_reader.add_file(asset.data)

            exch_reader = DataReader(cache)
            exch_reader.add_file(asset.data)
        else:
            data = __load_data(asset.data)
            local_reader = DataReader(cache)
            local_reader.add_data(data)

            exch_reader = DataReader(cache)
            exch_reader.add_data(data)

        local_market_depth = MarketDepth(asset.tick_size, asset.lot_size)
        exch_market_depth = MarketDepth(asset.tick_size, asset.lot_size)

        if asset.snapshot is not None:
            snapshot = __load_data(asset.snapshot)
            local_market_depth.apply_snapshot(snapshot)
            exch_market_depth.apply_snapshot(snapshot)

        local_state = state_init(
            asset.start_position,
            asset.start_balance,
            asset.start_fee,
            asset.maker_fee,
            asset.taker_fee,
            asset_type()
        )
        exch_state = state_init(
            asset.start_position,
            asset.start_balance,
            asset.start_fee,
            asset.maker_fee,
            asset.taker_fee,
            asset_type()
        )

        exch_to_local_orders = OrderBus()
        local_to_exch_orders = OrderBus()

        local = local_init(
            local_reader,
            local_to_exch_orders,
            exch_to_local_orders,
            local_market_depth,
            local_state,
            order_latency(),
            trade_list_size
        )
        if locals is None:
            locals = List.empty_list(typeof(local))
        locals.append(local)

        exch = exch_init(
            exch_reader,
            exch_to_local_orders,
            local_to_exch_orders,
            exch_market_depth,
            exch_state,
            order_latency(),
            queue_model()
        )
        if exchs is None:
            exchs = List.empty_list(typeof(exch))
        exchs.append(exch)

    return MultiAssetHftBacktest(locals, exchs)
