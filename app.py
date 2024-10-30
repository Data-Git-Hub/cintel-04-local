import plotly.express as px
from shiny.express import input, ui
from shinywidgets import render_plotly
from palmerpenguins import load_penguins
import seaborn as sns
import matplotlib.pyplot as plt
from shiny import render, reactive

# Load the palmerpenguins dataset
penguins = load_penguins()

# Set up the UI and layout
ui.page_opts(title="Penguins are Cool", fillable=True)

# Add a Shiny UI sidebar for user interaction
with ui.sidebar(open="open"):
    ui.h2("Sidebar")

    # Slider for filtering bill length data
    ui.input_slider("slider", "Max Bill Length (mm)", min=33, max=60, value=45)

    # Dropdown to choose a column attribute
    ui.input_selectize(
        "selected_attribute",
        "Choose an Attribute",
        ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )

    # Numeric input for number of Plotly histogram bins
    ui.input_numeric("plotly_bin_count", "Number of Plotly Bins", value=10)

    # Horizontal rule to separate sections
    ui.hr()

    # Slider for number of Seaborn bins
    ui.input_slider(
        "seaborn_bin_count", "Number of Seaborn Bins", min=5, max=50, value=20
    )

    # Checkbox group for species selection (affects only the scatter plot)
    ui.input_checkbox_group(
        "selected_species_list",
        "Select Species to Display in Scatterplot",
        ["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=True,
    )

    # Horizontal rule to separate sections
    ui.hr()

    # Add hyperlink to GitHub
    ui.a("Data-Git-Hub", href="https://github.com/Data-Git-Hub", target="_blank")

# Define layout with render_plotly outputs for vertical stacking
with ui.layout_columns():

    @render_plotly
    def plot1():
        # Use filtered_data() instead of penguins directly
        fig = px.histogram(
            filtered_data(),
            x="bill_length_mm",
            title="Penguins Bill Length Histogram",
        )
        fig.update_traces(marker_line_color="black", marker_line_width=1.5)
        return fig

    @render_plotly
    def plot2():
        # Get selected attribute and bin count for Plotly histogram
        selected_attribute = input.selected_attribute()
        bin_count = input.plotly_bin_count() if input.plotly_bin_count() else None

        # Plotly histogram for selected attribute
        fig = px.histogram(
            penguins,
            x=selected_attribute,
            title=f"Penguins {selected_attribute.replace('_', ' ').title()} Histogram",
            nbins=bin_count,
            color_discrete_sequence=["red"],
        )
        fig.update_traces(marker_line_color="black", marker_line_width=1.5)
        return fig


# Add the Seaborn histogram inside a card component
with ui.layout_columns():
    with ui.card():
        ui.card_header("Seaborn Histogram")

        @render.plot
        def plot3():
            fig, ax = plt.subplots()
            sns.histplot(
                data=penguins,
                x=input.selected_attribute(),
                bins=input.seaborn_bin_count(),
                hue="species",
                multiple="stack",
                ax=ax,
            )
            ax.set_title("Palmer Penguins by Species")
            ax.set_xlabel(input.selected_attribute())
            ax.set_ylabel("Number")
            return fig

    # Scatter plot positioned next to Seaborn histogram
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


# Display Data Table and Data Grid without selection or filters
with ui.layout_columns():
    with ui.card():
        ui.card_header("Data Table")

        @render.data_frame
        def penguins_table():
            return render.DataTable(penguins)  # Standard DataTable without filters

    with ui.card():
        ui.card_header("Data Grid")

        @render.data_frame
        def penguins_grid():
            return render.DataGrid(penguins, selection_mode="none")  # No row selection


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


# Add a reactive calculation to filter the data
@reactive.calc
def filtered_data():
    # Filter data based on selected species and bill length
    filtered = penguins[
        (penguins["bill_length_mm"] <= input.slider())
        & (penguins["species"].isin(input.selected_species_list()))
    ]
    return filtered
    #### correction made in notes.
