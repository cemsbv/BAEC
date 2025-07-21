import marimo

__generated_with = "0.14.12"
app = marimo.App(
    width="medium",
    app_title="BAEC",
    layout_file="layouts/gui_notebook.grid.json",
)


@app.cell
def _():
    import datetime
    import os

    import altair as alt
    import marimo as mo
    import numpy as np
    import pandas as pd
    from nuclei.client import NucleiClient

    from baec.measurements.io.basetime import BaseTimeBucket, Credentials
    from baec.measurements.measured_settlement_series import MeasuredSettlementSeries
    from baec.model.fitcore import (
        FitCoreModel,
        FitCoreModelGenerator,
        FitCoreParameters,
        FitCoreParametersBounds,
    )

    return (
        BaseTimeBucket,
        Credentials,
        FitCoreModel,
        FitCoreModelGenerator,
        FitCoreParameters,
        FitCoreParametersBounds,
        MeasuredSettlementSeries,
        NucleiClient,
        alt,
        datetime,
        mo,
        np,
        os,
        pd,
    )


@app.cell
def _(mo):
    jwt = mo.ui.text(placeholder="", label="NUCLEI JWT", kind="password")
    jwt
    return (jwt,)


@app.cell
def _(NucleiClient, jwt, os):
    if jwt.value != "":
        os.environ["NUCLEI_TOKEN"] = jwt.value
    client = NucleiClient()
    return (client,)


@app.cell
def _(mo):
    aws_access_key_id = mo.ui.text(placeholder="", label="BaseTime key ID", kind="text")
    aws_access_key_id
    return (aws_access_key_id,)


@app.cell
def _(mo):
    aws_secret_access_key = mo.ui.text(
        placeholder="", label="BaseTime key password", kind="password"
    )
    aws_secret_access_key
    return (aws_secret_access_key,)


@app.cell
def _(Credentials, aws_access_key_id, aws_secret_access_key):
    credentials = Credentials(
        aws_access_key_id=(
            aws_access_key_id.value if aws_access_key_id.value != "" else None
        ),
        aws_secret_access_key=(
            aws_secret_access_key.value if aws_secret_access_key.value != "" else None
        ),
    )
    return (credentials,)


@app.cell
def _(BaseTimeBucket, credentials):
    # create bucket manager
    manage_project = BaseTimeBucket(credentials)

    # get all the rod_id available to the user
    projects_ids = manage_project.get_users_projects_ids()
    return manage_project, projects_ids


@app.cell
def _(mo, projects_ids):
    # With search functionality
    project = mo.ui.dropdown(
        options=projects_ids.keys(),
        value=list(projects_ids.keys())[0],
        label="Project name",
        searchable=True,
        allow_select_none=False,
    )
    project
    return (project,)


@app.cell
def _(mo, project, projects_ids):
    # With search functionality
    rod_id = mo.ui.dropdown(
        options=projects_ids[project.value],
        value=projects_ids[project.value][0],
        label="Settlement rod",
        searchable=True,
        allow_select_none=False,
    )
    rod_id
    return (rod_id,)


@app.cell
def _(manage_project, project, rod_id):
    # create settlement rod measurement series from BaseTime Bucket
    measurements = manage_project.make_settlement_rod_measurement_series(
        project=project.value, rod_id=rod_id.value
    )
    return (measurements,)


@app.cell
def _(measurements, mo):
    start_date_time = mo.ui.date.from_series(
        measurements.to_dataframe()["date_time"], label="Start date"
    )
    start_date_time
    return (start_date_time,)


@app.cell
def _(alt, measurements, pd, start_date_time):
    _chart_1 = (
        alt.Chart(measurements.to_dataframe())
        .mark_line()
        .encode(
            x=alt.X(field="date_time", type="temporal", timeUnit="yearmonthdate"),
            y=alt.Y(field="rod_top_z", type="quantitative", aggregate="mean"),
            color=alt.value("blue"),
            tooltip=[
                alt.Tooltip(
                    field="date_time", timeUnit="yearmonthdate", title="date_time"
                ),
                alt.Tooltip(field="rod_top_z", aggregate="mean", format=",.2f"),
            ],
        )
    )
    _chart_2 = (
        alt.Chart(measurements.to_dataframe())
        .mark_line()
        .encode(
            x=alt.X(field="date_time", type="temporal", timeUnit="yearmonthdate"),
            y=alt.Y(field="ground_surface_z", type="quantitative", aggregate="mean"),
            color=alt.value("orange"),
            tooltip=[
                alt.Tooltip(
                    field="date_time", timeUnit="yearmonthdate", title="date_time"
                ),
                alt.Tooltip(field="ground_surface_z", aggregate="mean", format=",.2f"),
            ],
        )
    )
    _chart_3 = (
        alt.Chart(measurements.to_dataframe())
        .mark_line()
        .encode(
            x=alt.X(field="date_time", type="temporal", timeUnit="yearmonthdate"),
            y=alt.Y(field="rod_bottom_z", type="quantitative", aggregate="mean"),
            color=alt.value("green"),
            tooltip=[
                alt.Tooltip(
                    field="date_time", timeUnit="yearmonthdate", title="date_time"
                ),
                alt.Tooltip(field="rod_bottom_z", aggregate="mean", format=",.2f"),
            ],
        )
    )
    _rules = (
        alt.Chart(
            pd.DataFrame({"date_time": [start_date_time.value], "color": ["black"]})
        )
        .mark_rule()
        .encode(
            x=alt.X(field="date_time", type="temporal", timeUnit="yearmonthdate"),
            color=alt.Color("color:N", scale=None),
        )
    )
    (_chart_1 + _chart_2 + _chart_3 + _rules).resolve_scale()
    return


@app.cell
def _(measurements):
    measurements.to_dataframe()
    return


@app.cell
def _(measurements, mo):
    csv_download_lazy = mo.download(
        data=measurements.to_dataframe().to_csv(sep=";").encode("utf-8"),
        filename="measurements.csv",
        mimetype="text/csv",
        label="Download CSV",
    )
    csv_download_lazy
    return


@app.cell
def _(MeasuredSettlementSeries, datetime, measurements, start_date_time):
    series = MeasuredSettlementSeries(
        measurements,
        start_date_time=datetime.datetime.combine(
            start_date_time.value, measurements.to_dataframe()["date_time"].min().time()
        ),
    )
    return (series,)


@app.cell
def _(alt, pd, series):
    _chart_1 = (
        alt.Chart(
            pd.DataFrame(
                {"day": series.days, "fill_thicknesses": series.fill_thicknesses}
            )
        )
        .mark_line()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            y=alt.Y(field="fill_thicknesses", type="quantitative", aggregate="mean"),
            color=alt.value("blue"),
            tooltip=[
                alt.Tooltip(field="day", title="day"),
                alt.Tooltip(field="fill_thicknesses", aggregate="mean", format=",.2f"),
            ],
        )
    )
    _chart_2 = (
        alt.Chart(pd.DataFrame({"day": series.days, "settlements": series.settlements}))
        .mark_line()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            y=alt.Y(field="settlements", type="quantitative", aggregate="mean"),
            color=alt.value("orange"),
            tooltip=[
                alt.Tooltip(field="day", title="day"),
                alt.Tooltip(field="settlements", aggregate="mean", format=",.2f"),
            ],
        )
    )

    (_chart_1 + _chart_2).resolve_scale()
    return


@app.cell
def _(mo):
    primary_settlement_bounds = mo.ui.range_slider(
        start=0,
        stop=100,
        step=1,
        value=[0, 100],
        show_value=True,
        label="primary settlement [%]",
    )

    primary_settlement_bounds
    return (primary_settlement_bounds,)


@app.cell
def _(mo):
    shift_bounds = mo.ui.range_slider(
        start=0, stop=10, step=1, value=[0, 6], show_value=True, label="shift [days]"
    )

    shift_bounds
    return (shift_bounds,)


@app.cell
def _(mo):
    hydrodynamic_period_bounds = mo.ui.range_slider(
        start=0,
        stop=10,
        step=1,
        value=[0, 6],
        show_value=True,
        label="hydrodynamic period [year]",
    )

    hydrodynamic_period_bounds
    return (hydrodynamic_period_bounds,)


@app.cell
def _(mo):
    final_settlement_bounds = mo.ui.range_slider(
        start=0,
        stop=10,
        step=1,
        value=[0, 6],
        show_value=True,
        label="final settlement [m]",
    )
    final_settlement_bounds
    return (final_settlement_bounds,)


@app.cell
def _(
    FitCoreModelGenerator,
    FitCoreParameters,
    FitCoreParametersBounds,
    client,
    final_settlement_bounds,
    hydrodynamic_period_bounds,
    mo,
    np,
    primary_settlement_bounds,
    series,
    shift_bounds,
):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    params = FitCoreParameters(
        primarySettlement=FitCoreParametersBounds(*primary_settlement_bounds.value),
        shift=FitCoreParametersBounds(*shift_bounds.value),
        hydrodynamicPeriod=FitCoreParametersBounds(*hydrodynamic_period_bounds.value),
        finalSettlement=FitCoreParametersBounds(*final_settlement_bounds.value),
    )
    model = FitCoreModelGenerator(series=series, client=client, model_parameters=params)
    return (model,)


@app.cell
def _(mo, model, np, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    primary_settlement = mo.ui.number(
        start=0,
        step=1,
        value=model.fit().primarySettlement,
        label="primary settlement [%]",
    )

    primary_settlement
    return (primary_settlement,)


@app.cell
def _(mo, model, np, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    shift = mo.ui.number(start=0, step=1, value=model.fit().shift, label="shift [days]")

    shift
    return (shift,)


@app.cell
def _(mo, model, np, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    hydrodynamic_period = mo.ui.number(
        start=0,
        step=1,
        value=model.fit().hydrodynamicPeriod,
        label="hydrodynamic period [year]",
    )

    hydrodynamic_period
    return (hydrodynamic_period,)


@app.cell
def _(mo, model, np, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    final_settlement = mo.ui.number(
        start=0, step=1, value=model.fit().finalSettlement, label="final settlement [m]"
    )
    final_settlement
    return (final_settlement,)


@app.cell
def _(
    FitCoreModel,
    final_settlement,
    hydrodynamic_period,
    mo,
    model,
    np,
    primary_settlement,
    series,
    shift,
):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    model.set_model(
        FitCoreModel(
            primarySettlement=primary_settlement.value,
            shift=shift.value,
            hydrodynamicPeriod=hydrodynamic_period.value,
            finalSettlement=final_settlement.value,
        )
    )
    return


@app.cell
def _(mo):
    end_time_delta = mo.ui.number(
        start=0,
        step=10,
        value=100,
        label="End date of the predicted settlement  [days]",
    )
    end_time_delta
    return (end_time_delta,)


@app.cell
def _(end_time_delta, mo, model, np, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    days = np.arange(0, end_time_delta.value + 10, step=1, dtype=int)
    settlements = model.predict(days).settlement
    return days, settlements


@app.cell
def _(days, end_time_delta, mo, np, series, settlements):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    end_time_settlement = mo.ui.number(
        value=np.interp(end_time_delta.value, days, settlements).round(3),
        label=f"Settlement after {end_time_delta.value} days [m]",
        disabled=True
    )
    end_time_settlement
    return


@app.cell
def _(alt, days, end_time_delta, mo, np, pd, series, settlements):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    _chart_1 = (
        alt.Chart(
            pd.DataFrame(
                {"day": series.days, "fill_thicknesses": series.fill_thicknesses}
            )
        )
        .mark_line()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            y=alt.Y(field="fill_thicknesses", type="quantitative", aggregate="mean"),
            color=alt.value("blue"),
            tooltip=[
                alt.Tooltip(field="day", title="day"),
                alt.Tooltip(field="fill_thicknesses", aggregate="mean", format=",.2f"),
            ],
        )
    )
    _chart_2 = (
        alt.Chart(pd.DataFrame({"day": series.days, "settlements": series.settlements}))
        .mark_line()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            y=alt.Y(field="settlements", type="quantitative", aggregate="mean"),
            color=alt.value("orange"),
            tooltip=[
                alt.Tooltip(field="day", title="day"),
                alt.Tooltip(field="settlements", aggregate="mean", format=",.2f"),
            ],
        )
    )
    _chart_3 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "day": days,
                    "settlements": settlements,
                }
            )
        )
        .mark_line()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            y=alt.Y(field="settlements", type="quantitative", aggregate="mean"),
            color=alt.value("green"),
            tooltip=[
                alt.Tooltip(field="day", title="day"),
                alt.Tooltip(field="settlements", aggregate="mean", format=",.2f"),
            ],
        )
    )

    _rules = (
        alt.Chart(
            pd.DataFrame({"day": [end_time_delta.value], "color": ["black"]})
        )
        .mark_rule()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            color=alt.Color("color:N", scale=None),
        )
    )
    (_chart_1 + _chart_2 + _chart_3 + _rules).resolve_scale()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
