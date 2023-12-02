from pathlib import Path

from shiny import App, render, ui, reactive
import shinyswatch

from gym_schedule import MonthlySchedule



css_path = "style.css"


gym = MonthlySchedule("gym_calculation/exercises_acc.json",
                      "gym_calculation/exercises_prehab.json")


phases = {
    "Week 1": (f"Week 1: Accumulation ({gym.rpe[0]})", gym.main_week_one),
    "Week 2": (f"Week 2: Intensification ({gym.rpe[1]})", gym.main_week_two),
    "Week 3": (f"Week 3: Peaking ({gym.rpe[2]})", gym.main_week_three),
    "Week 4": (f"Week 4: Deload ({gym.rpe[3]})", gym.sessions_week_four)
}


headers = {
    "Week 1": gym.headers_main,
    "Week 2": gym.headers_main,
    "Week 3": gym.headers_main,
    "Week 4": gym.headers_deload
}


lifts = {0: "squats", 1: "bench", 2: "deadlift"}


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
                            list(phases.keys())),
            ui.input_action_button("btn_acc", "Change accessory lifts", class_="btn-primary"),
            ui.input_action_button("btn_pre", "Change prehab exercises", class_="btn-primary"),             
            ui.markdown("<br>"),
            ui.row(
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
        ui.row(
            ui.column(4,
                      ui.h5(ui.output_text("session_header1")),
                      ui.h6("Main lift"),
                      ui.output_table("main1"),
                      ui.h6("Accessory lifts"),
                      ui.h6("Prehab exercises")),
            ui.column(4,
                      ui.h5(ui.output_text("session_header2")), 
                      ui.h6("Main lift"),
                      ui.output_table("main2"),
                      ui.h6("Accessory lifts"),
                      ui.h6("Prehab exercises")),
            ui.column(4,
                      ui.h5(ui.output_text("session_header3")),
                      ui.h6("Main lift"),
                      ui.output_table("main3"),
                      ui.h6("Accessory lifts"),
                      ui.h6("Prehab exercises")),
            align="center"
        )
    )
)


def server(input, output, session):

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

    @reactive.Effect
    @reactive.event(input.btn_acc)
    def _():
        m = ui.modal(
            ui.input_select("acc_s", "Squats", gym.accessory.squats),
            ui.input_select("acc_b", "Bench", gym.accessory.bench),
            ui.input_select("acc_d", "Deadlift", gym.accessory.deadlift),
            title="Accessory Lifts",
            easy_close=False,
            size="m",
            footer=ui.modal_button("Select"),
        )
        ui.modal_show(m)

    @reactive.Effect
    @reactive.event(input.btn_pre)
    def _():
        m = ui.modal(
            ui.input_select("pre_s", "Squats", gym.prehab.squats),
            ui.input_select("pre_b", "Bench", gym.prehab.bench),
            ui.input_select("pre_d", "Deadlift", gym.prehab.deadlift),
            title="Accessory Lifts",
            easy_close=False,
            size="m",
            footer=ui.modal_button("Select"),
        )
        ui.modal_show(m)

    #@reactive.Effect
    #@reactive.event(input.btn_pre)


app = App(app_ui, server)
