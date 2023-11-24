from pathlib import Path

from shiny import App, render, ui
import shinyswatch

from gym_schedule import MonthlySchedule


gym = MonthlySchedule()

phases = {"Accumulation": ("Week 1: Accumulation", gym.week_one),
"Intensification": ("Week 2: Intensification", gym.week_two),
"Peaking": ("Week 3: Peaking", gym.week_three),
"Deloading": ("Week 4: Deloading", gym.week_four)}


lifts = {0: "squats", 1: "bench", 2: "deadlift"}


app_ui = ui.page_fluid(
    shinyswatch.theme.minty(),
    ui.markdown("<br>"),
    ui.row(
        ui.column(
            6,
            ui.panel_title("Sara's Workout Schedule"),
        ),
        ui.column(
            6,
            ui.popover(
                ui.input_action_button("btn", "Info", class_="btn-outline-primary"),
                "I'm not a professional trainer and this is not a recommendation. "
                "This is just for my own personal use.",
                id="btn_popover",
            ),
            align="right")),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("gym_phase",
                            "Select the current phase",
                            list(phases.keys())),
            ui.hr(),
            width="300px"
        ),
        ui.row(
            ui.h3(ui.output_text("phase")),
            align="center"
        ),
        ui.row(
            ui.column(4, ui.h5(ui.output_text("session_header1")), ui.output_table("session1")),
            ui.column(4, ui.h5(ui.output_text("session_header2")), ui.output_table("session2")),
            ui.column(4, ui.h5(ui.output_text("session_header3")), ui.output_table("session3")),
            align="center"
        )
    )
)


def server(input, output, session):
    @output
    @render.text
    def session_header1():
        if input.gym_phase() == "Deloading":
            return "Full body session"
        else:
            return "Squats session"

    @output
    @render.text
    def session_header2():
        if input.gym_phase() == "Deloading":
            return "Upper body session"
        else:
            return "Bench session"

    @output
    @render.text
    def session_header3():
        if input.gym_phase() == "Deloading":
            return "Lower body session"
        else:
            return "Deadlift session"

    @output
    @render.text
    def phase():
        return phases[input.gym_phase()][0]

    @output
    @render.table
    def session1():
        if input.gym_phase() == "Deloading":
            df = phases[input.gym_phase()][1].full_body_session()
        else:
            df = phases[input.gym_phase()][1].generate_sessions()[0]
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @output
    @render.table
    def session2():
        if input.gym_phase() == "Deloading":
            df = phases[input.gym_phase()][1].upper_body_session()
        else:
            df = phases[input.gym_phase()][1].generate_sessions()[1]
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))

    @output
    @render.table
    def session3():
        if input.gym_phase() == "Deloading":
            df = phases[input.gym_phase()][1].lower_body_session()
        else:
            df = phases[input.gym_phase()][1].generate_sessions()[2]
        return (df.style
                .set_table_attributes('class="dataframe table shiny-table w-auto"')
                .hide(axis="index")
                .hide(axis="columns"))


app = App(app_ui, server)
