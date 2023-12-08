from dataclasses import dataclass
import json
from typing import Dict, Optional, List, Union

import numpy as np
import pandas as pd


class GymSchedule:

    def __init__(self,
                 main_set_reps: Optional[int] = None,
                 accessory_set_reps: Optional[int] = None) -> None:

        self.main_lifts = ["squats", "bench", "deadlift"]

        self.secondary_lifts = {
            "squats": "deadlift",
            "bench": "squats",
            "deadlift": "bench",
        }

        if main_set_reps is not None:
            self.sets_main = GymSchedule.generate_sets(
                warmup_sets=4,
                working_sets=3,
                ending_reps=1,
                max_reps=main_set_reps)
        else:
            self.sets_main = None

        if accessory_set_reps is not None:
            self.sets_accessory = GymSchedule.generate_sets(
                warmup_sets=2,
                working_sets=3,
                ending_reps=1,
                max_reps=accessory_set_reps)
        else:
            self.sets_accessory = None

    @staticmethod
    def generate_sets(warmup_sets: int,
                      working_sets: int,
                      ending_reps: int,
                      max_reps: int,
                      starting_with_bar: bool = True) -> Union[str, List[str]]:
        if starting_with_bar:
            sets = ["1x5"]
        else:
            sets = []
        sets += [f"1x{j}" for i, j in zip(range(warmup_sets),
                                np.linspace(4, ending_reps, warmup_sets, dtype=int))]
        sets += [f"{working_sets}x{max_reps}"]
        if len(sets) == 1:
             return sets[0]
        return sets
    
    def generate_main(self, main_lift: str) -> pd.DataFrame:
        sets = [(main_lift, i) for i in self.sets_main]
        return pd.DataFrame(sets, columns=["lift", "setup"])

    def generate_secondary(self, main_lift: str) -> pd.DataFrame:
        lift = self.secondary_lifts[main_lift]
        sets = [(lift, i) for i in self.sets_accessory]
        return pd.DataFrame(sets, columns=["lift", "setup"])

    def generate_acc(self, main_lift: str):
        acc = [k for k in self.main_lifts if k not in [self.secondary_lifts[main_lift], main_lift]][0]
        sets = []
        for i in self.sets_accessory:
            sets.append((acc, i))
        return pd.DataFrame(sets, columns=["lift", "setup"])


class DeloadSchedule(GymSchedule):

    def __init__(self) -> None:
        super().__init__()

    def full_body_session(self):
        # 2 sets of 5 reps at 50-60% of 1RM
        sets = GymSchedule.generate_sets(
            warmup_sets=0,
            working_sets=2,
            ending_reps=5,
            max_reps=5)
        session = []
        for m in self.main_lifts:
            for s in sets:
                session.append((m, s))
        prehab = [
            "Hip exercises (variations)",
            "Scapular Retraction",
            "Band Pull-Aparts",
        ]
        for p in prehab:
            session.append((p, ""))

        return pd.DataFrame(session, columns=["lift", "setup"])
    
    def _prehab_session(self, exercises: List[str]) -> pd.DataFrame:
        return pd.DataFrame(exercises, columns=["lift"])

    def upper_body_session(self):
        exercises = [
            "Prone YTI Raises",
            "Reverse Prayer Hands",
            "Jefferson Curls",
            "Side Lateral Shoulder Raises",
            "Triceps Pushdowns",
            "Lat Pulldowns",
            "Rows",
            "Machine Reverse Fly",
            "Bicep curls",
        ]
        return self._prehab_session(exercises)

    def lower_body_session(self):
        exercises = [
            "Deadbugs",
            "Fire Hydrant",
            "Glute Bridges (variations)",
            "Clamshells",
            "Bird Dog",
            "Kettlebell Swings",
            "Calf Raises",
            "Kickbacks",
            "Leg Extension",
        ]
        return self._prehab_session(exercises)
