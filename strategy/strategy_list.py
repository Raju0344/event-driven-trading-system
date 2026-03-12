from .sma_strategy import MovingAverageCrossStrategy
from .mrp_strategy import MeanRevertingPairStrategy

strategy_dict = {"sma": MovingAverageCrossStrategy, "mrp":MeanRevertingPairStrategy}