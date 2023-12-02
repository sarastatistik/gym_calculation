from typing import Dict, Optional, List, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel


class WeightManager(BaseModel):
    weight_increase: float
    prc_squats: List[float]
    prc_bench: List[float]
    prc_deadlift: List[float]
    prc_working: List[float]
    prc_deload: float
    starting_weights: Dict[str, Union[int, float]]
    starting_weights_deload: Dict[str, Union[int, float]]


class WeightCalc:
    def __init__(self,
                 weight_manager: WeightManager,
                 squats: Union[int, float],
                 bench: Union[int, float],
                 deadlift: Union[int, float],
                 accessory_lifts: Optional[Dict[str, Union[int, float]]] = None,
                 warmup_sets: int = 5) -> None:
        
        self.weight_manager = weight_manager
        
        self.warmup_sets = warmup_sets
        self.accessory_lifts = accessory_lifts

        self.weights = {
            "squats": squats,
            "bench": bench,
            "deadlift": deadlift
        }

        self._setup_weights()
    
    def _get_warmup_weights(self, lift: str, x: Union[float, int]):
        # FIXME: ugly hardcoding
        if lift != "bench":
            y = np.linspace(self.weight_manager.starting_weights[lift], x, self.warmup_sets)
            y = [self._round_set(i) for i in y]
            y = [round(i, -1) if i < 40 else i for i in y]
        else:
            y = np.linspace(self.weight_manager.starting_weights[lift] + 10, x, self.warmup_sets - 1)
            y = [self.weight_manager.starting_weights[lift]] + [self._round_set(i) for i in y]
        return y

    def _setup_weights(self):
        self.one_rep = {
            "squats": [self._round_set(x * self.weights["squats"]) for x in self.weight_manager.prc_squats],
            "bench": [self._round_set(x * self.weights["bench"]) for x in self.weight_manager.prc_bench],
            "deadlift": [self._round_set(x * self.weights["deadlift"]) for x in self.weight_manager.prc_deadlift]
        }
        self.working_weights = {
            "squats": [self._round_set(x * y) for x, y in zip(self.one_rep["squats"], self.weight_manager.prc_working)],
            "bench": [self._round_set(x * y) for x, y in zip(self.one_rep["bench"], self.weight_manager.prc_working)],
            "deadlift": [self._round_set(x * y) for x, y in zip(self.one_rep["deadlift"], self.weight_manager.prc_working)]
        }

        self.warmup_weights = {}
        for k in self.one_rep.keys():
            self.warmup_weights[k] = [self._get_warmup_weights(k, x) for x in self.one_rep[k]]
        
        self.deload_weights = {
            "squats": [self.weight_manager.starting_weights_deload["squats"]] + [self._round_set(self.weight_manager.prc_deload * self.weights["squats"])]*2,
            "bench": [self.weight_manager.starting_weights_deload["bench"]] + [self._round_set(self.weight_manager.prc_deload * self.weights["bench"])]*2,
            "deadlift": [self.weight_manager.starting_weights_deload["deadlift"]] + [self._round_set(self.weight_manager.prc_deload * self.weights["deadlift"])]*2
        }

    def _round_set(self, x: Union[int, float]):
        # Based on 2.5
        y = round(x, -1) - 10
        y = [y + self.weight_manager.weight_increase*i for i in range(10)]
        z = [abs(i - x) for i in y]
        z = np.where(pd.Series(z) == min(z))[0][0]        
        return y[z]

    def update_squats(self, x: Union[float, int]):
        self.weights["squats"] = x
        self._setup_weights()

    def update_bench(self, x: Union[float, int]):
        self.weights["bench"] = x
        self._setup_weights()

    def update_deadlift(self, x: Union[float, int]):
        self.weights["deadlift"] = x
        self._setup_weights()

    def get_weights(self, lift: str):
        w = []
        for x, y in zip(self.warmup_weights[lift], self.working_weights[lift]):
            w.append(x + [y])
        return w
