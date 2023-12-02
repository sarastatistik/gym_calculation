from dataclasses import dataclass
import json
from typing import Dict, Optional, List, Union

import numpy as np
import pandas as pd




class WeightCalc:
    def __init__(self,
                 squats: Union[int, float],
                 bench: Union[int, float],
                 deadlift: Union[int, float],
                 warmup_sets: int = 5) -> None:
        
        self.weight_increase = 2.5
        self.warmup_sets = warmup_sets

        self.prc = {
            "squats": [0.7, 0.8, 0.9],
            "bench": [0.85, 0.9, 0.975],
            "deadlift": [0.8, 0.87, 0.95]
        }

        self.working_prc = [0.8, 0.85, 0.9]

        self.weights = {
            "squats": squats,
            "bench": bench,
            "deadlift": deadlift
        }
        self.starting_weights = {
            "squats": 20,
            "bench": 20,
            "deadlift": 60
        }

        self._setup_weights()
    
    def _get_warmup_weights(self, lift: str, x: Union[float, int]):
        if lift != "bench":
            y = np.linspace(self.starting_weights[lift], x, self.warmup_sets)
            y = [self._round_set(i) for i in y]
            y = [round(i, -1) if i < 40 else i for i in y]
        else:
            y = np.linspace(self.starting_weights[lift] + 10, x, self.warmup_sets - 1)
            y = [self.starting_weights[lift]] + [self._round_set(i) for i in y]
        return y

    def _setup_weights(self):
        self.one_rep = {
            "squats": [self._round_set(x * self.weights["squats"]) for x in self.prc["squats"]],
            "bench": [self._round_set(x * self.weights["bench"]) for x in self.prc["bench"]],
            "deadlift": [self._round_set(x * self.weights["deadlift"]) for x in self.prc["deadlift"]]
        }
        self.working_weights = {
            "squats": [self._round_set(x * y) for x, y in zip(self.one_rep["squats"], self.working_prc)],
            "bench": [self._round_set(x * y) for x, y in zip(self.one_rep["bench"], self.working_prc)],
            "deadlift": [self._round_set(x * y) for x, y in zip(self.one_rep["deadlift"], self.working_prc)]
        }

        self.warmup_weights = {}
        for k in self.one_rep.keys():
            self.warmup_weights[k] = [self._get_warmup_weights(k, x) for x in self.one_rep[k]]
        
        self.deload_weights = {
            "squats": [20] + [self._round_set(0.6 * self.weights["squats"])]*2,
            "bench": [20] + [self._round_set(0.6 * self.weights["bench"])]*2,
            "deadlift": [40] + [self._round_set(0.6 * self.weights["deadlift"])]*2
        }

    def _round_set(self, x: Union[int, float]):
        # Based on 2.5
        y = round(x, -1) - 10
        y = [y + self.weight_increase*i for i in range(10)]
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
    


class GymSchedule:

    def __init__(self,
                 main_set_reps: Optional[int] = None,
                 accessory_set_reps: Optional[int] = None) -> None:

        self.main_lifts = ["squats", "bench", "deadlift"]

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
                warmup_sets=3,
                working_sets=3,
                ending_reps=2,
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

    def generate_acc(self, main_lift: str):
        acc = [k for k in self.main_lifts if k != main_lift]
        sets = []
        for i in acc:
            for j in self.sets_accessory:
                sets.append((i, j))
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
   

# one: accumulation
# two: intensification
# three: peaking
# four: deloading





class ExerciseBucket:

    def __init__(self,
                 squats: List[str], 
                 bench: List[str],
                 deadlift: List[str]) -> None:
        self.squats = squats
        self.bench = bench
        self.deadlift = deadlift
        self.all = squats + bench + deadlift


class MonthlySchedule:

    def __init__(self, accessory: str, prehab: str, weight_calc: WeightCalc) -> None:
        self.weight_calc = weight_calc
        
        self.weight_calc.get_weights("bench")
        self.weight_calc.get_weights("deadlift")


        self.prc = ["70%", "80%", "90%", "55%"]
        self.headers_main = ["Squats session", "Bench session", "Deadlift session"]
        self.headers_deload = ["Full body session", "Upper body session", "Lower Body Session"]

        with open(accessory, "r", encoding="utf-8") as f:
            self.accessory = ExerciseBucket(**json.load(f))


        with open(prehab, "r", encoding="utf-8") as f:
            self.prehab = ExerciseBucket(**json.load(f))

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


gym = MonthlySchedule("gym_calculation/exercises_acc.json",
                       "gym_calculation/exercises_prehab.json",
                       weight_calc=WeightCalc(70, 47.5, 102.5))





self = gym

