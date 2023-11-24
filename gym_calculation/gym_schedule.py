from typing import Dict, Optional, List, Union

import numpy as np
import pandas as pd


class GymSchedule:

    def __init__(self,
                 main_set_reps: Optional[int] = None,
                 accessory_set_reps: Optional[int] = None,
                 prehab_set_reps: int = 6,
                 accessory_lifts: Optional[Dict[str, str]] = None,
                 prehab_lifts: Optional[Dict[str, str]] = None) -> None:

        self.main_lifts = ["squats", "bench", "deadlift"]

        if accessory_lifts is None:
            accessory_lifts = {k: f"acc-{k}" for k in self.main_lifts}

        if prehab_lifts is None:
            prehab_lifts = {k: f"prehab-{k}" for k in self.main_lifts}

        self.accessory_lifts = accessory_lifts
        self.prehab_lifts = prehab_lifts

        if main_set_reps is not None:
            self.sets_main = GymSchedule.generate_sets(
                warmup_sets=3,
                working_sets=3,
                ending_reps=1,
                max_reps=main_set_reps)
        else:
            self.sets_main = None

        if accessory_set_reps is not None:
            self.sets_accessory = GymSchedule.generate_sets(
                warmup_sets=2,
                working_sets=3,
                ending_reps=2,
                max_reps=accessory_set_reps)
        else:
            self.sets_accessory = None

        self.sets_prehab = GymSchedule.generate_sets(
            warmup_sets=0,
            working_sets=3,
            ending_reps=0,
            max_reps=prehab_set_reps,
            starting_with_bar=False
        )

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
    
    def _generate_session(self, main_lift: str) -> pd.DataFrame:
        sets = [(main_lift, i) for i in self.sets_main]
        acc = [v for k, v in self.accessory_lifts.items() if k != main_lift]
        for i in acc:
            for j in self.sets_accessory:
                sets.append((i, j))            
        sets.append((self.prehab_lifts[main_lift], self.sets_prehab))
        sets = pd.DataFrame(sets, columns=["lift", "setup"])
        return sets
    
    def generate_sessions(self) -> List[pd.DataFrame]:
        return [self._generate_session(m) for m in self.main_lifts]


class DeloadSchedule(GymSchedule):

    def __init__(self,
                 prehab_set_reps: int = 8) -> None:
        super().__init__(prehab_set_reps=prehab_set_reps)

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
        for p in self.prehab_lifts.values():
            session.append((p, self.sets_prehab))
        return pd.DataFrame(session, columns=["lift", "setup"])
    
    def _prehab_session(self, exercises: List[str]) -> pd.DataFrame:
        session = [(e, self.sets_prehab) for e in exercises]
        return pd.DataFrame(session, columns=["lift", "setup"])

    def upper_body_session(self):
        exercises = [
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
            "Bridges",
            "Single Leg Bridge",
            "Bird Dog",
            "Kickbacks",
            "Leg Extension",
        ]
        return self._prehab_session(exercises)
   

# one: accumulation
# two: intensification
# three: peaking
# four: deloading



class MonthlySchedule:

    def __init__(self) -> None:
        self.week_one = GymSchedule(main_set_reps=8, accessory_set_reps=6)
        self.week_two = GymSchedule(main_set_reps=5, accessory_set_reps=4)
        self.week_three = GymSchedule(main_set_reps=2, accessory_set_reps=1)
        self.week_four = DeloadSchedule(prehab_set_reps=8)


self = MonthlySchedule()





