from typing import Dict, List

import pandas as pd
from pydantic import BaseModel
from shiny import App, render, ui, reactive
import shinyswatch


from create_schedule import MonthlySchedule



class AppHelper(BaseModel):
    gym_schedule: MonthlySchedule
    css_path: str
    headers_week: Dict[int, List[str]]
    headers_session: Dict[int, List[str]]


gym = MonthlySchedule("gym_calculation/params/weight_manager.json",
                      "gym_calculation/params/exercises_acc.json",
                      "gym_calculation/params/exercises_prehab.json",
                      [70, 47.5, 102.5])


css_path = "gym_calculation/params/style.css"


phases = {
    "Week 1": (f"Week 1: Accumulation ({gym.prc[0]})", gym.main_week_one, gym.acc_week_one),
    "Week 2": (f"Week 2: Intensification ({gym.prc[1]})", gym.main_week_two, gym.acc_week_two),
    "Week 3": (f"Week 3: Peaking ({gym.prc[2]})", gym.main_week_three, gym.acc_week_three),
    "Week 4": (f"Week 4: Deload ({gym.prc[3]})", gym.sessions_week_four)
}


headers = {
    "Week 1": gym.headers_main,
    "Week 2": gym.headers_main,
    "Week 3": gym.headers_main,
    "Week 4": gym.headers_deload
}


week123 = ui.row(
            ui.column(4,
                      ui.h5(ui.output_text("session_header1")),
                      ui.markdown("*15 min warmup*"),
                      ui.h6("Main lift"),
                      ui.output_table("main1"),
                      ui.h6("Accessory lifts"),
                      ui.output_table("acc1"),
                      ui.h6("Prehab exercises"),
                      ui.output_table("pre1")),
            ui.column(4,
                      ui.h5(ui.output_text("session_header2")), 
                      ui.markdown("*15 min warmup*"),
                      ui.h6("Main lift"),
                      ui.output_table("main2"),
                      ui.h6("Accessory lifts"),
                      ui.output_table("acc2"),
                      ui.h6("Prehab exercises"),
                      ui.output_table("pre2")),
            ui.column(4,
                      ui.h5(ui.output_text("session_header3")),
                      ui.markdown("*15 min warmup*"),
                      ui.h6("Main lift"),
                      ui.output_table("main3"),
                      ui.h6("Accessory lifts"),
                      ui.output_table("acc3"),
                      ui.h6("Prehab exercises"),
                      ui.output_table("pre3")),
            align="center"
        )




week4 = ui.row(
            ui.column(4,
                      ui.h5(ui.output_text("session_header1")),
                      ui.markdown("*15 min warmup*"),
                      ui.output_table("main1")),
            ui.column(4,
                      ui.h5(ui.output_text("session_header2")),
                      ui.markdown("*15 min warmup*"), 
                      ui.output_table("main2")),
            ui.column(4,
                      ui.h5(ui.output_text("session_header3")),
                      ui.markdown("*15 min warmup*"),
                      ui.output_table("main3")),
            align="center"
        )


app_ui = ui.page_fluid(
    shinyswatch.theme.minty(),
    ui.include_css(css_path),
    ui.markdown("<br>"),
    ui.row(
        ui.column(
            6,
            ui.h2("Sara's Workout Schedule"),
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
    ui.layout_sidebar(
        ui.sidebar(
            ui.h5("Select the current phase:"),
            ui.input_select("gym_phase",
                            "",
                            list(phases.keys()),
                            selected="Week 1"),
            ui.input_action_button("btn_acc", "Change accessory lifts", class_="btn-primary"),
            ui.input_action_button("btn_pre", "Change prehab exercises", class_="btn-primary"),             
            ui.markdown("<br>"),
            ui.row(
                "detta filter gör inget nu - ändrar sen vikt i schema",
                ui.h5("Fill out 1RM for each lift:"),
                ui.column(4, ui.input_numeric("rm1_s", "Squats", 70, min=20, step=2.5)),
                ui.column(4, ui.input_numeric("rm1_b", "Bench", 47.5, min=20, step=2.5)),
                ui.column(4, ui.input_numeric("rm1_d", "Deadlift", 102.5, min=20, step=2.5))
            ),
            width="400px"
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

    @output
    @render.ui
    def ui_main_part():
        if input.gym_phase() == "Week 4":
            return week4
        else:
            return week123

    @output
    @render.text
    def phase():
        return phases[input.gym_phase()][0]

    @output
    @render.text
    def session_header1():
        return headers[input.gym_phase()][0]

    @output
    @render.text
    def session_header2():
        return headers[input.gym_phase()][1]

    @output
    @render.text
    def session_header3():
        return headers[input.gym_phase()][2]

    @output
    @render.table
    def main1():
        df = phases[input.gym_phase()][1]()[0]
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @output
    @render.table
    def main2():
        df = phases[input.gym_phase()][1]()[1]
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @output
    @render.table
    def main3():
        df = phases[input.gym_phase()][1]()[2]
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))
    @output
    @render.table
    def acc1():
        if input.gym_phase() != "Week 4":
            df = phases[input.gym_phase()][2]()[0]
            df.loc[df["lift"] == "bench", "lift"] = acc_bench()
            df.loc[df["lift"] == "deadlift", "lift"] = acc_deadlift()
            return (df.style
                    .set_table_attributes('class="dataframe table shiny-table w-auto"')
                    .hide(axis="index")
                    .hide(axis="columns"))

    @output
    @render.table
    def acc2():
        if input.gym_phase() != "Week 4":
            df = phases[input.gym_phase()][2]()[1]
            df.loc[df["lift"] == "squats", "lift"] = acc_squats()
            df.loc[df["lift"] == "deadlift", "lift"] = acc_deadlift()
            return (df.style
                    .set_table_attributes('class="dataframe table shiny-table w-auto"')
                    .hide(axis="index")
                    .hide(axis="columns"))

    @output
    @render.table
    def acc3():
        if input.gym_phase() != "Week 4":
            df = phases[input.gym_phase()][2]()[2]
            df.loc[df["lift"] == "bench", "lift"] = acc_bench()
            df.loc[df["lift"] == "squats", "lift"] = acc_squats()
            return (df.style
                    .set_table_attributes('class="dataframe table shiny-table w-auto"')
                    .hide(axis="index")
                    .hide(axis="columns"))
        
    @output
    @render.table
    def pre1():
        df = pd.DataFrame(pre_squats())
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @output
    @render.table
    def pre2():
        df = pd.DataFrame(pre_bench())
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @output
    @render.table
    def pre3():
        df = pd.DataFrame(pre_deadlift())
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @reactive.Effect
    @reactive.event(input.btn_acc)
    def _():
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
    def _():
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
    def _():
        new = input.acc_s()
        acc_squats.set(new)


    @reactive.Effect
    @reactive.event(input.acc_b)
    def _():
        new = input.acc_b()
        acc_bench.set(new)

    @reactive.Effect
    @reactive.event(input.acc_d)
    def _():
        new = input.acc_d()
        acc_deadlift.set(new)

    @reactive.Effect
    @reactive.event(input.pre_s)
    def _():
        new = input.pre_s()
        pre_squats.set(new)

    @reactive.Effect
    @reactive.event(input.pre_b)
    def _():
        new = input.pre_b()
        pre_bench.set(new)

    @reactive.Effect
    @reactive.event(input.pre_d)
    def _():
        new = input.pre_d()
        pre_deadlift.set(new)


app = App(app_ui, server)
