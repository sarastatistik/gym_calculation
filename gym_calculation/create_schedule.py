from dataclasses import dataclass
import json
from typing import Dict, Optional, List, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel

from gym_schedule import GymSchedule, DeloadSchedule
from weight_calc import WeightCalc, WeightManager


# one: accumulation
# two: intensification
# three: peaking
# four: deloading


class ExerciseBucket(BaseModel):
    squats: List[str]
    bench: List[str]
    deadlift: List[str]


class MonthlySchedule:

    def __init__(self, weight_manager:str, accessory: str, prehab: str, weights: List[Union[int, float]]) -> None:

        # TODO: Lägg till i weight manager istället så det blir rätt
        self.prc = ["70%", "80%", "90%", "55%"]
        
        self.headers_main = ["Squats session", "Bench session", "Deadlift session"]
        self.headers_deload = ["Full body session", "Upper body session", "Lower Body Session"]

        with open(weight_manager, "r", encoding="utf-8") as f:
            weight_manager = WeightManager(**json.load(f))

        with open(accessory, "r", encoding="utf-8") as f:
            self.accessory = ExerciseBucket(**json.load(f))

        with open(prehab, "r", encoding="utf-8") as f:
            self.prehab = ExerciseBucket(**json.load(f))

        self.weight_calc = WeightCalc(weight_manager, weights[0], weights[1], weights[2])
        
        self.weight_calc.get_weights("bench")
        self.weight_calc.get_weights("deadlift")


        self.accumulation = GymSchedule(main_set_reps=8, accessory_set_reps=6)
        self.intensification = GymSchedule(main_set_reps=5, accessory_set_reps=4)
        self.peaking = GymSchedule(main_set_reps=2, accessory_set_reps=1)
        self.deloading = DeloadSchedule()

    @staticmethod
    def rename_main_lifts(df: pd.DataFrame):
        df.loc[df["lift"] == "squats", "lift"] = "Squats"
        df.loc[df["lift"] == "bench", "lift"] = "Bench Press"
        df.loc[df["lift"] == "deadlift", "lift"] = "Deadlift"
        return df
   
    def main_week_one(self):
        d = [self.accumulation.generate_main(m) for m in self.accumulation.main_lifts]
        w = [self.weight_calc.get_weights(lift)[0] for lift in ["squats", "bench", "deadlift"]]
        for x, y in zip(d, w):
            x.insert(2, "weight", y)
            x["weight"] = [str(round(i,1)) if str(i)[-1] != "0" else str(round(i)) for i in x["weight"]]
            x["weight"] = [i + "kg" for i in x["weight"]]
        return [MonthlySchedule.rename_main_lifts(df) for df in d]

    def main_week_two(self):
        d = [self.intensification.generate_main(m) for m in self.intensification.main_lifts]
        w = [self.weight_calc.get_weights(lift)[1] for lift in ["squats", "bench", "deadlift"]]
        for x, y in zip(d, w):
            x.insert(2, "weight", y)
            x["weight"] = [str(round(i,1)) if str(i)[-1] != "0" else str(round(i)) for i in x["weight"]]
            x["weight"] = [i + "kg" for i in x["weight"]]
        return [MonthlySchedule.rename_main_lifts(df) for df in d]

    def main_week_three(self):
        d = [self.peaking.generate_main(m) for m in self.peaking.main_lifts]
        w = [self.weight_calc.get_weights(lift)[2] for lift in ["squats", "bench", "deadlift"]]
        for x, y in zip(d, w):
            x.insert(2, "weight", y)
            x["weight"] = [str(round(i,1)) if str(i)[-1] != "0" else str(round(i)) for i in x["weight"]]
            x["weight"] = [i + "kg" for i in x["weight"]]
        return [MonthlySchedule.rename_main_lifts(df) for df in d]
    
    def acc_week_one(self):
        d = [self.accumulation.generate_acc(m) for m in self.accumulation.main_lifts]
        return d

    def acc_week_two(self):
        d = [self.intensification.generate_acc(m) for m in self.intensification.main_lifts]
        return d

    def acc_week_three(self):
        d = [self.peaking.generate_acc(m) for m in self.peaking.main_lifts]
        return d

    def sessions_week_four(self):
        d = [self.deloading.full_body_session(), self.deloading.upper_body_session(), self.deloading.lower_body_session()]
        return [MonthlySchedule.rename_main_lifts(df) for df in d]








gym = MonthlySchedule("gym_calculation/params/weight_manager.json",
                      "gym_calculation/params/exercises_acc.json",
                      "gym_calculation/params/exercises_prehab.json",
                      [70, 47.5, 102.5])





self = gym

