import marimo

__generated_with = "0.14.17"
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
    import micropip
    import numpy as np
    import pandas as pd
    return alt, datetime, micropip, mo, np, os, pd


@app.cell
async def _(micropip):
    await micropip.install("baec")

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
    _colors = alt.Scale(domain=["rod_top_z", "ground_surface_z", "rod_bottom_z"], range=['blue', 'orange', 'green'])

    _chart_1 = (
        alt.Chart(measurements.to_dataframe())
        .transform_fold(
            ['rod_top_z', 'ground_surface_z', 'rod_bottom_z'],
            as_=['variable', 'value']
        )
        .mark_line()
        .encode(
            x=alt.X(field="date_time", type="temporal", timeUnit="yearmonthdate", title="Date"),
            y=alt.Y(field="value", type="quantitative", title="Measurements [m NAP]"),
            color=alt.Color('variable:N', scale=_colors, title="Legend"),
            tooltip=[
                alt.Tooltip(
                    field="date_time", timeUnit="yearmonthdate", title="Date"
                ),
                alt.Tooltip(field="value", format=",.2f", title="Value"),
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
    (_chart_1 + _rules).resolve_scale()
    return


@app.cell
def _(measurements, mo):
    csv_download_lazy_measurements = mo.download(
        data=measurements.to_dataframe().to_csv(sep=";").encode("utf-8"),
        filename="measurements.csv",
        mimetype="text/csv",
        label="Download CSV",
    )
    csv_download_lazy_measurements
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
        start=0, step=0.01, value=model.fit().finalSettlement, label="final settlement [m]"
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
def _(end_time_delta, mo, model, np, pd, series, shift, start_date_time):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    days = np.arange(0, end_time_delta.value + 1, step=1, dtype=int) + shift.value
    settlements = model.predict(days).settlement

    _df_left = pd.DataFrame(
                {
                    "days": series.days,
                    "fill_thicknesses": series.fill_thicknesses,
                    "settlements": np.array(series.settlements) * -1,
                    "merge": (np.round(series.days, 3)*100).astype(int)
                }
            )

    _df_right = pd.DataFrame(
                {
                    "days": days,
                    "predict": np.array(settlements) * -1,
                    "merge": (np.round(days, 3)*100).astype(int)
                }
            )

    _df = pd.merge(_df_right, _df_left, on="merge", how = 'outer')
    _df["days_merge"] = _df["merge"] / 100
    _df["date_time"] = pd.to_timedelta(_df["days_merge"], unit="day") + pd.to_datetime(start_date_time.value)
    df_settlements_preditions = _df.interpolate(limit_direction="backward")
    return days, df_settlements_preditions, settlements


@app.cell
def _(days, end_time_delta, mo, np, series, settlements):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    end_time_settlement = mo.ui.number(
        value=np.interp(end_time_delta.value, days, np.array(settlements).astype(np.float64)).round(3),
        label=f"Settlement after {end_time_delta.value} days [m]",
        disabled=True
    )
    end_time_settlement
    return


@app.cell
def _(alt, df_settlements_preditions, end_time_delta, pd):
    _colors = alt.Scale(domain=["fill_thicknesses",], range=['blue'])

    _chart_1 = (
        alt.Chart(df_settlements_preditions)
        .transform_fold(
            ["fill_thicknesses"],
            as_=['variable', 'value']
        )
        .mark_line()
        .encode(
            x=alt.X(field="days_merge", type="quantitative", title="Days", scale=alt.Scale(type='symlog')),
            y=alt.Y(field="value", type="quantitative", title="Measurements [m]"),
            color=alt.Color('variable:N', scale=_colors, title="Legend"),
            tooltip=[
                alt.Tooltip(
                    field="date_time", title="Date"
                ),
                alt.Tooltip(
                    field="days_merge", title="Days"
                ),
                alt.Tooltip(field="value", format=",.2f", title="Value"),
            ],
        )
    )

    _rules_1 = (
        alt.Chart(
            pd.DataFrame({"day": [end_time_delta.value], "color": ["black"]})
        )
        .mark_rule()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            color=alt.Color("color:N", scale=None),
        )
    )


    (_chart_1 + _rules_1).resolve_scale()
    return


@app.cell
def _(alt, df_settlements_preditions, end_time_delta, pd):
    _colors = alt.Scale(domain=["settlements", "predict"], range=['orange', 'green'])

    _chart_2 = (
        alt.Chart(df_settlements_preditions)
        .transform_fold(
            ["settlements", "predict"],
            as_=['variable', 'value']
        )
        .mark_line()
        .encode(
            x=alt.X(field="days_merge", type="quantitative", title="Days", scale=alt.Scale(type='symlog')),
            y=alt.Y(field="value", type="quantitative", title="Measurements [m]"),
            color=alt.Color('variable:N', scale=_colors, title="Legend"),
            tooltip=[
                alt.Tooltip(
                    field="date_time", title="Date"
                ),
                alt.Tooltip(
                    field="days_merge", title="Days"
                ),
                alt.Tooltip(field="value", format=",.2f", title="Value"),
            ],
        )
    )


    _rules_1 = (
        alt.Chart(
            pd.DataFrame({"day": [end_time_delta.value], "color": ["black"]})
        )
        .mark_rule()
        .encode(
            x=alt.X(field="day", type="quantitative"),
            color=alt.Color("color:N", scale=None),
        )
    )


    (_chart_2 + _rules_1).resolve_scale()
    return


@app.cell
def _(df_settlements_preditions, mo):
    csv_download_lazy_prediction = mo.download(
        data=df_settlements_preditions.to_csv(sep=";").encode("utf-8"),
        filename="measurements.csv",
        mimetype="text/csv",
        label="Download CSV",
    )
    csv_download_lazy_prediction
    return


if __name__ == "__main__":
    app.run()
