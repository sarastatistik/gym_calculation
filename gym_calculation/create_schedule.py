from dataclasses import dataclass
import json
from typing import Dict, Optional, List, Union

import numpy as np
import pandas as pd
from pydantic import BaseModel

from gym_schedule import GymSchedule, DeloadSchedule


# one: accumulation
# two: intensification
# three: peaking
# four: deloading


class ExerciseBucket(BaseModel):
    squats: List[str]
    bench: List[str]
    deadlift: List[str]


class MonthlySchedule:

    def __init__(self, accessory: str, prehab: str) -> None:

        with open(accessory, "r", encoding="utf-8") as f:
            self.accessory = ExerciseBucket(**json.load(f))

        with open(prehab, "r", encoding="utf-8") as f:
            self.prehab = ExerciseBucket(**json.load(f))

        self.accumulation = GymSchedule(main_set_reps=8, accessory_set_reps=6)
        self.intensification = GymSchedule(main_set_reps=5, accessory_set_reps=4)
        self.peaking = GymSchedule(main_set_reps=2, accessory_set_reps=1)
        self.deloading = DeloadSchedule()

        self.main_lifts = self.accumulation.main_lifts
        self.sets_main = len(self.accumulation.sets_main)
        self.sets_sec = len(self.accumulation.sets_accessory)
        self.secondary_lifts = self.accumulation.secondary_lifts
    
    def _setup_df(self, df: pd.DataFrame):
        df.loc[df["lift"] == "squats", "lift"] = "Squats"
        df.loc[df["lift"] == "bench", "lift"] = "Bench"
        df.loc[df["lift"] == "deadlift", "lift"] = "Deadlift"
        return df
    
    def _setup_exercise(self, set_method: GymSchedule, lift: str):
        df = set_method(lift)
        return self._setup_df(df)

    def main_part(self):
        return [[self._setup_exercise(gym_class.generate_main, m) for m in self.main_lifts]
                for gym_class in [self.accumulation, self.intensification, self.peaking]]

    def secondary_part(self):
        return [[self._setup_exercise(gym_class.generate_secondary, m) for m in self.main_lifts]
                for gym_class in [self.accumulation, self.intensification, self.peaking]]

    def sessions_week_four(self):
        f = self.deloading.full_body_session()
        d = [f, self.deloading.upper_body_session(), self.deloading.lower_body_session()]
        return [self._setup_df(df) for df in d]
