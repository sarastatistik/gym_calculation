import json
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
    starting_weights_deload: Dict[str, Union[int, float]]


class WeightCalc:
    def __init__(self,
                 weight_manager: str,
                 s: Union[float, int], b: Union[float, int], d: Union[float, int],
                 s0: Union[float, int], b0: Union[float, int], d0: Union[float, int],
                 warmup_sets: int = 4,
                 warmup_sets_sec: int = 3) -> None:
        
        with open(weight_manager, "r", encoding="utf-8") as f:
            self.weight_manager = WeightManager(**json.load(f))
 
        self.warmup_sets = warmup_sets
        self.warmup_sets_sec = warmup_sets_sec

        self.one_rm = {
            "squats": s,
            "bench": b,
            "deadlift": d
        }
        self.starting_weights = {
            "squats": s0,
            "bench": b0,
            "deadlift": d0
        }

        self.prc = {
            "squats": self.weight_manager.prc_squats,
            "bench": self.weight_manager.prc_bench,
            "deadlift": self.weight_manager.prc_deadlift
        }

        self.lifts = list(self.one_rm.keys())

        self._setup_weights()
    
    def _setup_weights(self):
        # Main lifts
        one_rep = {
            k: [self._round_set(x * self.one_rm[k]) for x in self.prc[k]] for k in self.lifts
        }
        self.weights = {}
        for k in self.lifts:
            w = []
            for x, y in zip(one_rep[k], self.weight_manager.prc_working):
                self._round_set(x * y)
                w.append(self._get_warmup_weights(k, x, self.warmup_sets) + [self._round_set(x * y)])
            self.weights[k] = w

        # Secondary lifts
        one_rep_sec = {
            k: [self._round_set(i*0.9) for i in one_rep[k]] for k in self.lifts
        }
        self.weights_sec = {}
        for k in self.lifts:
            w = []
            for x, y in zip(one_rep_sec[k], self.weights[k]):
                w.append(self._get_warmup_weights(k, x, self.warmup_sets_sec) + [self._round_set(y[-1]*0.9725)])
            self.weights_sec[k] = w

        # Deload week weights        
        self.deload_weights = {}
        for k in self.lifts:
            self.deload_weights[k] = [self.weight_manager.starting_weights_deload[k]] + [self._round_set(self.weight_manager.prc_deload * self.one_rm[k])]

    def _round_set(self, x: Union[int, float]):
        # Based on 2.5
        y = round(x, -1) - 10
        y = [y + self.weight_manager.weight_increase*i for i in range(10)]
        z = [abs(i - x) for i in y]
        z = np.where(pd.Series(z) == min(z))[0][0]        
        return y[z]

    def _get_warmup_weights(self, lift: str, x: Union[float, int], s: int):
        # FIXME: ugly hardcoding
        if lift != "bench":
            y = np.linspace(self.starting_weights[lift], x, s)
            y = [self._round_set(i) for i in y]
            y = [round(i, -1) if i < 40 else i for i in y]
        else:
            y = np.linspace(self.starting_weights[lift] + 10, x, s - 1)
            y = [self.starting_weights[lift]] + [self._round_set(i) for i in y]
        return y

    def get_weights(self, lift: str, main: bool = True):
        if main:
            return self.weights[lift]
        else:
            return self.weights_sec[lift]

    @staticmethod
    def _format_weight(w: Union[int, float]) -> str:
        if isinstance(w, int):
            return f"{w}kg"
        else:
            return f"{round(w)}kg" if str(w)[-1] == "0" else f"{round(w, 1)}kg"
