import os
os.environ['TCL_LIBRARY'] = r"C:\Program Files\Python313\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Program Files\Python313\tcl\tk8.6"

import plotly.express as px
from shiny import App, ui, render, reactive, Inputs
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from palmerpenguins import load_penguins

plt.switch_backend('Agg')

# Load the palmerpenguins dataset
penguins = load_penguins()

# Define the server logic
def server(Inputs, output, session):
    # Reactive function for filtered data based on the slider input (for testing with Matplotlib)
    @reactive.Calc
    def filtered_data():
        return penguins[penguins["bill_length_mm"] <= Inputs.slider()]

    # Define a simpler `plot1` using Matplotlib
    def plot1():
        fig, ax = plt.subplots()
        data = filtered_data()
        ax.hist(data["bill_length_mm"], bins=30, color='skyblue', edgecolor='black')
        ax.set_title("Penguins Bill Length Histogram (Matplotlib Version)")
        ax.set_xlabel("Bill Length (mm)")
        ax.set_ylabel("Frequency")
        return fig

    output.plot1 = render.plot(plot1)

    # Define Plot2: Histogram for selected attribute (still using Matplotlib)
    @output
    @render.plot
    def plot2():
        fig, ax = plt.subplots()
        attribute = Inputs.selected_attribute()
        ax.hist(penguins[attribute], bins=Inputs.plotly_bin_count(), color='red', edgecolor='black')
        ax.set_title(f"Penguins {attribute.replace('_', ' ').title()} Histogram (Matplotlib Version)")
        ax.set_xlabel(attribute.replace('_', ' ').title())
        ax.set_ylabel("Frequency")
        return fig

    # Seaborn histogram (plot3) remains unchanged
    def plot3():
        fig, ax = plt.subplots()
        sns.histplot(
            data=penguins,
            x="bill_length_mm",
            bins=Inputs.seaborn_bin_count(),
            hue="species",
            multiple="stack",
            ax=ax
        )
        ax.set_title("Palmer Penguins by Species")
        ax.set_xlabel("Bill Length (mm)")
        ax.set_ylabel("Number")
        return fig

    output.plot3 = render.plot(plot3)

    # Reactive function to filter data based on selected species for scatterplot
    @reactive.Calc
    def filtered_df():
        selected_species = Inputs.species()
        return penguins[penguins["species"].isin(selected_species)]

    # Define the Seaborn scatterplot (length_depth)
    @output
    @render.plot
    def length_depth():
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=filtered_df(),
            x="bill_length_mm",
            y="bill_depth_mm",
            hue="species",
            ax=ax
        )
        ax.set_title("Scatterplot: Bill Length vs. Bill Depth by Species")
        ax.set_xlabel("Bill Length (mm)")
        ax.set_ylabel("Bill Depth (mm)")
        return fig

    # Data Tab: Reactive function to filter data based on body mass
    @reactive.Calc
    def filtered_data_table():
        return penguins[penguins["body_mass_g"] <= Inputs.body_mass_slider()]

    # Render Data Table with filtered penguins dataset
    @output
    @render.data_frame
    def penguins_table():
        return filtered_data_table()

    # Reactive function to filter data based on year range
    @reactive.Calc
    def filtered_data_grid():
        start_year, end_year = Inputs.year_range_slider()
        return penguins[(penguins["year"] >= start_year) & (penguins["year"] <= end_year)]

    # Render Data Grid with filtered penguins dataset
    @output
    @render.data_frame
    def penguins_grid():
        return filtered_data_grid()

# Define the UI layout
app_ui = ui.page_fluid(
    ui.navset_pill(
        ui.nav_panel("Graphics", ui.layout_sidebar(
            ui.sidebar(
                ui.h2("Sidebar"),
                ui.input_slider("slider", "Max Bill Length (mm)", min=33, max=60, value=45),
                ui.input_selectize("selected_attribute", "Choose an Attribute", choices=[
                    "bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"
                ]),
                ui.input_numeric("plotly_bin_count", "Number of Bins for Plot2", value=10),
                ui.hr(),
                ui.input_slider("seaborn_bin_count", "Number of Seaborn Bins", min=5, max=50, value=20),
                ui.input_checkbox_group(
                    "species",
                    "Select Species",
                    ["Adelie", "Gentoo", "Chinstrap"],
                    selected=["Adelie", "Gentoo", "Chinstrap"]
                ),
                ui.hr(),
                ui.a("Data-Git-Hub", href="https://github.com/Data-Git-Hub", target="_blank")
            ),
            ui.div(
                ui.output_plot("plot1"),
                ui.output_plot("plot2"),
                ui.output_plot("plot3"),
                ui.output_plot("length_depth")
            )
        )),
        ui.nav_panel("Data", ui.layout_sidebar(
            ui.sidebar(
                ui.h2("Sidebar"),
                ui.input_slider("body_mass_slider", "Filter by Body Mass (g)",
                    min=penguins["body_mass_g"].min(),
                    max=penguins["body_mass_g"].max(),
                    value=penguins["body_mass_g"].mean()
                ),
                ui.input_slider("year_range_slider", "Filter by Year", min=2007, max=2009, value=(2007, 2009))
            ),
            ui.div(
                ui.card(
                    ui.card_header("Data Table"),
                    ui.output_data_frame("penguins_table")
                ),
                ui.card(
                    ui.card_header("Data Grid"),
                    ui.output_data_frame("penguins_grid")
                )
            )
        ))
    )
)

# Create the app
app = App(app_ui, server)
app.run()

