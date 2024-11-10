import os
os.environ['TCL_LIBRARY'] = r"C:\Program Files\Python313\tcl\tcl8.6"
os.environ['TK_LIBRARY'] = r"C:\Program Files\Python313\tcl\tk8.6"
import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly
from palmerpenguins import load_penguins
import seaborn as sns
import matplotlib.pyplot as plt
from shiny import render, reactive

# Load the palmerpenguins dataset
penguins = load_penguins()

# Set up the UI with tabs and sidebar layout
ui.page_opts(title="Penguins are Cool", fillable=True)

with ui.navset_pill(id="tab"):
    # Graphics tab with sidebar layout
    with ui.nav_panel("Graphics"):
        with ui.layout_sidebar():
            with ui.sidebar(open="open", bg="#f8f8f8"):
                ui.h2("Sidebar")
                ui.input_slider(
                    "slider", "Max Bill Length (mm)", min=33, max=60, value=45
                )
                ui.input_selectize(
                    "selected_attribute",
                    "Choose an Attribute",
                    [
                        "bill_length_mm",
                        "bill_depth_mm",
                        "flipper_length_mm",
                        "body_mass_g",
                    ],
                )
                ui.input_numeric(
                    "plotly_bin_count", "Number of Plotly Bins", value=10
                )
                ui.hr()
                ui.input_slider(
                    "seaborn_bin_count",
                    "Number of Seaborn Bins",
                    min=5,
                    max=50,
                    value=20,
                )
                ui.input_checkbox_group(
                    "selected_species_list",
                    "Select Species to Display in Scatterplot",
                    ["Adelie", "Gentoo", "Chinstrap"],
                    selected=["Adelie", "Gentoo", "Chinstrap"],
                    inline=True,
                )
                ui.hr()
                ui.a(
                    "Data-Git-Hub",
                    href="https://github.com/Data-Git-Hub",
                    target="_blank",
                )

            # Main content area for plots
            with ui.layout_columns():
                # Define a reactive function for filtered data
                @reactive.Calc
                def filtered_data():
                    return penguins[penguins["bill_length_mm"] <= input.slider()]

                @render_plotly
                def plot1():
                    fig = px.histogram(
                        filtered_data(),
                        x="bill_length_mm",
                        title="Penguins Bill Length Histogram",
                    )
                    fig.update_traces(marker_line_color="black", marker_line_width=1.5)
                    return fig

                # Plot2: Attribute Histogram, affected by "Choose an Attribute"
                @render_plotly
                def plot2():
                    selected_attribute = input.selected_attribute()
                    bin_count = (
                        input.plotly_bin_count() if input.plotly_bin_count() else None
                    )
                    fig = px.histogram(
                        penguins,
                        x=selected_attribute,
                        title=f"Penguins {selected_attribute.replace('_', ' ').title()} Histogram",
                        nbins=bin_count,
                        color_discrete_sequence=["red"],
                    )
                    fig.update_traces(marker_line_color="black", marker_line_width=1.5)
                    return fig

            # Seaborn histogram in a card, unaffected by "Choose an Attribute"
            with ui.layout_columns():
                with ui.card():
                    ui.card_header("Seaborn Histogram")

                    @render.plot
                    def plot3():
                        fig, ax = plt.subplots()
                        sns.histplot(
                            data=penguins,
                            x="bill_length_mm",  # Fixed attribute for Seaborn histogram
                            bins=input.seaborn_bin_count(),
                            hue="species",
                            multiple="stack",
                            ax=ax,
                        )
                        ax.set_title("Palmer Penguins by Species")
                        ax.set_xlabel("Bill Length (mm)")
                        ax.set_ylabel("Number")
                        return fig

                # Scatter plot in a card, unaffected by "Choose an Attribute"
                with ui.card():
                    ui.card_header("Plotly Scatterplot: Species")

                    @render_plotly
                    def plotly_scatterplot():
                        filtered_penguins = penguins[
                            penguins["species"].isin(input.selected_species_list())
                        ]
                        fig = px.scatter(
                            filtered_penguins,
                            x="body_mass_g",
                            y="bill_depth_mm",
                            color="species",
                            title="Penguins Scatterplot: Body Mass vs. Bill Depth",
                            labels={
                                "body_mass_g": "Body Mass (g)",
                                "bill_depth_mm": "Bill Depth (mm)",
                            },
                        )
                        return fig

    # Data tab with Data Table and Data Grid
    with ui.nav_panel("Data"):
        with ui.layout_sidebar():
            with ui.sidebar(open="open", bg="#f8f8f8"):
                ui.h2("Sidebar")
                # Slider to filter the Data Table by Body Mass
                ui.input_slider(
                    "body_mass_slider",
                    "Filter by Body Mass (g)",
                    min=penguins["body_mass_g"].min(),
                    max=penguins["body_mass_g"].max(),
                    value=penguins["body_mass_g"].mean(),
                )
                # Range slider to filter the Data Grid by year
                ui.input_slider(
                    "year_range_slider",
                    "Filter by Year",
                    min=2007,
                    max=2009,
                    value=(2007, 2009),
                )

            # Layout for Data Table and Data Grid
            with ui.layout_columns():
                with ui.card():
                    ui.card_header("Data Table")

                    # Reactive calculation to filter data based on body mass
                    @reactive.Calc
                    def filtered_data_table():
                        return penguins[
                            penguins["body_mass_g"] <= input.body_mass_slider()
                        ]

                    # Render DataTable with filtered penguins dataset
                    @render.data_frame
                    def penguins_table():
                        return render.DataTable(filtered_data_table())

                with ui.card():
                    ui.card_header("Data Grid")

                    # Reactive calculation to filter data based on year range
                    @reactive.Calc
                    def filtered_data_grid():
                        start_year, end_year = input.year_range_slider()
                        return penguins[
                            (penguins["year"] >= start_year)
                            & (penguins["year"] <= end_year)
                        ]

                    # Render DataGrid with filtered penguins dataset
                    @render.data_frame
                    def penguins_grid():
                        return render.DataGrid(filtered_data_grid())
