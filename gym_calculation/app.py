from typing import Dict, List, Union
from htmltools import Tag

import pandas as pd
from pydantic import BaseModel
from shiny import App, render, ui, reactive
import shinyswatch

from create_schedule import MonthlySchedule
from weight_calc import WeightCalc


START = 1


class AppHelper(BaseModel):
    css_path: str
    id2week: Dict[int, str]
    headers_week: Dict[int, str]
    headers_sessions: Dict[int, str]
    headers_deload: Dict[int, str]
    path_weight_manager: str
    path_exercises_acc: str
    path_exercises_prehab: str


a = {
    "css_path": "gym_calculation/params/style.css",
    "id2week": {0: "Week 1", 1: "Week 2", 2: "Week 3", 3: "Week 4"},
    "headers_week": {0: "Week 1: Accumulation", 1: "Week 2: Intensification", 2: "Week 3: Peaking", 3: "Week 4: Deload"},
    "headers_sessions": {0: "Squats session", 1: "Bench session", 2: "Deadlift session"},
    "headers_deload": {0: "Full body session", 1: "Upper body session", 2: "Lower Body Session"},
    "path_weight_manager": "gym_calculation/params/weight_manager.json",
    "path_exercises_acc": "gym_calculation/params/exercises_acc.json",
    "path_exercises_prehab": "gym_calculation/params/exercises_prehab.json"
}


app_helper = AppHelper(**a)


gym = MonthlySchedule(app_helper.path_exercises_acc,
                      app_helper.path_exercises_prehab)


phases = {
    "Week 1": (gym.main_part()[0], gym.secondary_part()[0]),
    "Week 2": (gym.main_part()[1], gym.secondary_part()[1]),
    "Week 3": (gym.main_part()[2], gym.secondary_part()[2]),
    "Week 4": (gym.sessions_week_four)
}

def setup_weigth_calc(s: Union[float, int], b: Union[float, int], d: Union[float, int],
                      s0: Union[float, int], b0: Union[float, int], d0: Union[float, int]) -> WeightCalc:
    return WeightCalc(
        s=s, b=b, d=d,
        s0=s0, b0=b0, d0=d0,
        weight_manager=app_helper.path_weight_manager,
        warmup_sets=(gym.sets_main - 1),
        warmup_sets_sec=(gym.sets_sec - 1)
    )


app_ui = ui.page_fluid(
    shinyswatch.theme.minty(),
    ui.include_css(app_helper.css_path),
    ui.markdown("<br>"),
    ui.row(
        ui.column(
            6,
            ui.h1("Sara's Workout Schedule"),
        ),
        ui.column(
            6,
            ui.popover(
                ui.input_action_button("btn", "Info", class_="btn-primary"),
                "I'm not a professional trainer and this is not a recommendation. "
                "This is just for my own personal use.",
                id="btn_popover",
            ),
            align="right")),
    ui.markdown("<br>"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h5("Select the current phase:"),
            ui.input_select("gym_phase",
                            "",
                            list(app_helper.id2week.values()),
                            selected=app_helper.id2week[START]),
            ui.input_action_button("btn_acc", "Change accessory lifts", class_="btn-primary"),
            ui.input_action_button("btn_pre", "Change prehab exercises", class_="btn-primary"),             
            ui.markdown("<br>"),

            ui.row(
                ui.h4("Starting weights:"),
                ui.column(4, ui.input_numeric("sw_s", "Squats", 20, min=20, max=70, step=10)),
                ui.column(4, ui.input_numeric("sw_b", "Bench", 20, min=20, max=70, step=10)),
                ui.column(4, ui.input_numeric("sw_d", "Deadlift", 60, min=40, max=70, step=10))
            ),

            ui.row(
                ui.h4("1RM for each lift:"),
                ui.column(4, ui.input_numeric("rm1_s", "Squats", 70, min=20, step=2.5)),
                ui.column(4, ui.input_numeric("rm1_b", "Bench", 47.5, min=20, step=2.5)),
                ui.column(4, ui.input_numeric("rm1_d", "Deadlift", 102.5, min=20, step=2.5))
            ),

    ui.markdown("""
    
    1. <h6>Accumulation</h6> Higher volume and moderate intensity for muscle indurance
    2. <h6>Intensification</h6> Lower volume and higher intensity
    3. <h6>Peaking</h6> Very low volume and close to maximum strength
    4. <h6>Deload</h6> Reduced volume and intensity to regenerate
    """),
    
            width="450px"
        ),
        {"style": "background-color: #fff"},
        ui.row(
            ui.h3(ui.output_text("phase")),
            align="center"
        ),
        ui.output_ui("ui_main_part")
    )
)


def server(input, output, session):

    acc_squats = reactive.Value(gym.accessory.squats[0])
    acc_bench = reactive.Value(gym.accessory.bench[0])
    acc_deadlift = reactive.Value(gym.accessory.deadlift[0])
    pre_squats = reactive.Value(gym.prehab.squats[:2])
    pre_bench = reactive.Value(gym.prehab.bench[:2])
    pre_deadlift = reactive.Value(gym.prehab.deadlift[:2])

    week2id = {k: v for k, v in zip(app_helper.id2week.values(), app_helper.id2week.keys())}



    def get_session_columns(n: int, deload: bool = False) -> Tag:
        if deload:
            return ui.column(4,
                ui.h4(ui.output_text(f"session_header{n}")),
                ui.markdown("*15 min warmup*"),
                ui.output_table(f"main{n}"))
        else:
            return ui.column(4,
                ui.h4(ui.output_text(f"session_header{n}")),
                ui.markdown("*15 min warmup*"),
                ui.h6("Main lift"),
                ui.output_table(f"main{n}"),
                ui.h6("Secondary lift"),
                ui.output_table(f"sec{n}"),
                ui.h6("Accessory lift"),
                ui.output_table(f"acc{n}"),
                ui.h6("Prehab exercises"),
                ui.output_table(f"pre{n}")
                )

    @output
    @render.ui
    def ui_main_part():
        if input.gym_phase() == "Week 4":
            return ui.row(
                get_session_columns(1, deload=True),
                get_session_columns(2, deload=True),
                get_session_columns(3, deload=True),
                align="center")

        else:
            return ui.row(
                get_session_columns(1),
                get_session_columns(2),
                get_session_columns(3),
                align="center")

    @output
    @render.text
    def phase():
        nonlocal week2id
        return app_helper.headers_week[week2id[input.gym_phase()]]

    @output
    @render.text
    def session_header1():
        if input.gym_phase() == app_helper.id2week[3]:
            return app_helper.headers_deload[0]
        else:
            return app_helper.headers_sessions[0]

    @output
    @render.text
    def session_header2():
        if input.gym_phase() == app_helper.id2week[3]:
            return app_helper.headers_deload[1]
        else:
            return app_helper.headers_sessions[1]

    @output
    @render.text
    def session_header3():
        if input.gym_phase() == app_helper.id2week[3]:
            return app_helper.headers_deload[2]
        else:
            return app_helper.headers_sessions[2]

    @output
    @render.table
    def main1():
        nonlocal week2id
        wc = setup_weigth_calc(s=input.rm1_s(), b=input.rm1_b(), d=input.rm1_d(),
                               s0=input.sw_s(), b0=input.sw_b(), d0=input.sw_d())
        
        if input.gym_phase() != "Week 4":
            df = phases[input.gym_phase()][0][0]
            w = [wc._format_weight(i) for i in wc.get_weights("squats")[week2id[input.gym_phase()]]]
        else:
            df = phases[input.gym_phase()]()[0]
            w = []
            for m in gym.main_lifts:
                for j in [wc._format_weight(i) for i in wc.deload_weights[m]]:
                    w.append(j)
            w += [""] * 3
        df["weight"] = w
        return df

    @output
    @render.table
    def main2():
        wc = setup_weigth_calc(s=input.rm1_s(), b=input.rm1_b(), d=input.rm1_d(),
                               s0=input.sw_s(), b0=input.sw_b(), d0=input.sw_d())
        nonlocal week2id

        if input.gym_phase() != "Week 4":
            df = phases[input.gym_phase()][0][1]
            w = [wc._format_weight(i) for i in wc.get_weights("bench")[week2id[input.gym_phase()]]]
            df["weight"] = w
        else:
            df = phases[input.gym_phase()]()[1]
        return df

    @output
    @render.table
    def main3():
        wc = setup_weigth_calc(s=input.rm1_s(), b=input.rm1_b(), d=input.rm1_d(),
                               s0=input.sw_s(), b0=input.sw_b(), d0=input.sw_d())
        nonlocal week2id

        if input.gym_phase() != "Week 4":
            df = phases[input.gym_phase()][0][2]
            w = [wc._format_weight(i) for i in wc.get_weights("deadlift")[week2id[input.gym_phase()]]]
            df["weight"] = w

        else:
            df = phases[input.gym_phase()]()[2]
        return df

    @output
    @render.table
    def sec1():
        nonlocal week2id
        if input.gym_phase() != "Week 4":  # NOTE: to get around error
            wc = setup_weigth_calc(s=input.rm1_s(), b=input.rm1_b(), d=input.rm1_d(),
                                   s0=input.sw_s(), b0=input.sw_b(), d0=input.sw_d())
            df = phases[input.gym_phase()][1][0]
            w = [wc._format_weight(i) for i in wc.get_weights("deadlift", False)[week2id[input.gym_phase()]]]
            df["weight"] = w
            return df

    @output
    @render.table
    def sec2():
        nonlocal week2id
        if input.gym_phase() != "Week 4":
            wc = setup_weigth_calc(s=input.rm1_s(), b=input.rm1_b(), d=input.rm1_d(),
                                   s0=input.sw_s(), b0=input.sw_b(), d0=input.sw_d())
            df = phases[input.gym_phase()][1][1]
            w = [wc._format_weight(i) for i in wc.get_weights("deadlift", False)[week2id[input.gym_phase()]]]
            df["weight"] = w
            return df

    @output
    @render.table
    def sec3():
        nonlocal week2id
        if input.gym_phase() != "Week 4":
            wc = setup_weigth_calc(s=input.rm1_s(), b=input.rm1_b(), d=input.rm1_d(),
                                   s0=input.sw_s(), b0=input.sw_b(), d0=input.sw_d())
            df = phases[input.gym_phase()][1][2]
            w = [wc._format_weight(i) for i in wc.get_weights("deadlift", False)[week2id[input.gym_phase()]]]
            df["weight"] = w
            return df

    @output
    @render.table
    def acc1():
        return pd.DataFrame([acc_bench()])

    @output
    @render.table
    def acc2():
        return pd.DataFrame([acc_deadlift()])

    @output
    @render.table
    def acc3():
        return pd.DataFrame([acc_squats()])

    @output
    @render.table
    def pre1():
        return pd.DataFrame(pre_squats())

    @output
    @render.table
    def pre2():
        return pd.DataFrame(pre_bench())

    @output
    @render.table
    def pre3():
        return pd.DataFrame(pre_deadlift())

    @reactive.Effect
    @reactive.event(input.btn_acc)
    def _effect_change_acc():
        m = ui.modal(
            ui.input_select("acc_s", "Squats", gym.accessory.squats, selected=acc_squats()),
            ui.input_select("acc_b", "Bench", gym.accessory.bench, selected=acc_bench()),
            ui.input_select("acc_d", "Deadlift", gym.accessory.deadlift, selected=acc_deadlift()),
            title="Accessory Lifts",
            easy_close=True,
            size="m"
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.btn_pre)
    def _effect_change_pre():
        m = ui.modal(
            ui.input_select("pre_s", "Squats", gym.prehab.squats, selected=pre_squats(), selectize=True, multiple=True),
            ui.input_select("pre_b", "Bench", gym.prehab.bench, selected=pre_bench(), selectize=True, multiple=True),
            ui.input_select("pre_d", "Deadlift", gym.prehab.deadlift, selected=pre_deadlift(), selectize=True, multiple=True),
            title="Prehab Exercises",
            easy_close=True,
            size="m"
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.acc_s)
    def _effect_select():
        new = input.acc_s()
        acc_squats.set(new)

    @reactive.Effect
    @reactive.event(input.acc_b)
    def _effect_select():
        new = input.acc_b()
        acc_bench.set(new)

    @reactive.Effect
    @reactive.event(input.acc_d)
    def _effect_select():
        new = input.acc_d()
        acc_deadlift.set(new)

    @reactive.Effect
    @reactive.event(input.pre_s)
    def _effect_select():
        new = input.pre_s()
        pre_squats.set(new)

    @reactive.Effect
    @reactive.event(input.pre_b)
    def _effect_select():
        new = input.pre_b()
        pre_bench.set(new)

    @reactive.Effect
    @reactive.event(input.pre_d)
    def _effect_select():
        new = input.pre_d()
        pre_deadlift.set(new)


app = App(app_ui, server)
