import marimo

__generated_with = "0.14.17"
app = marimo.App(
    width="full",
    app_title="BAEC",
    layout_file="layouts/app.grid.json",
)


@app.cell
def _():
    import datetime
    import os
    import sys

    import altair as alt
    import micropip
    import numpy as np
    import pandas as pd

    import marimo as mo

    return alt, datetime, micropip, mo, np, os, pd, sys


@app.cell
async def _(micropip, sys):
    if sys.platform == "emscripten":
        # running in Pyodide or other Emscripten based build
        await micropip.install(["pyodide-http", "baec[aws]", "ssl"])

        # Patch requests
        import pyodide_http

        pyodide_http.patch_all()

    from nuclei.client import NucleiClient

    from baec.measurements.io.basetime import BaseTimeBucket, Credentials
    from baec.measurements.measured_settlement_series import (
        MeasuredSettlementSeries,
    )
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

    if "NUCLEI_TOKEN" in os.environ:
        client = NucleiClient()
    else:
        raise ValueError("No JWT token provided")
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
def _(Credentials, aws_access_key_id, aws_secret_access_key, os):
    if aws_access_key_id.value != "":
        os.environ["BASETIME_KEY_ID"] = aws_access_key_id.value

    if aws_secret_access_key.value != "":
        os.environ["BASETIME_ACCESS_KEY"] = aws_secret_access_key.value

    if "BASETIME_KEY_ID" in os.environ and "BASETIME_ACCESS_KEY" in os.environ:
        credentials = Credentials()

    else:
        raise ValueError("BaseTime AWS credentials provided")
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
    _options = sorted(list(projects_ids.keys()))
    project = mo.ui.dropdown(
        options=_options,
        value=_options[0],
        label="Project name",
        searchable=True,
        allow_select_none=False,
    )
    project
    return (project,)


@app.cell
def _(mo, project, projects_ids):
    # With search functionality
    _options = sorted(projects_ids[project.value])
    rod_id = mo.ui.dropdown(
        options=_options,
        value=_options[0],
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

    df_measurements = measurements.to_dataframe()
    df_measurements = df_measurements.set_index("date_time", drop=False)
    df_measurements = df_measurements.resample("1W").max()
    return df_measurements, measurements


@app.cell
def _(df_measurements, mo, np):
    _message = mo.md("")
    if all(np.isnan(df_measurements["rod_bottom_z"])):
        _message = mo.md(
            ":warning: **No measurements**, please select a defferent settlement rod."
        )
    _message
    return


@app.cell
def _(df_measurements, mo):
    start_date_time = mo.ui.date.from_series(
        df_measurements["date_time"], label="Start date"
    )
    start_date_time
    return (start_date_time,)


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
def _(
    MeasuredSettlementSeries,
    datetime,
    df_measurements,
    measurements,
    start_date_time,
):
    series = MeasuredSettlementSeries(
        measurements,
        start_date_time=datetime.datetime.combine(
            start_date_time.value, df_measurements["date_time"].min().time()
        ),
    )
    return (series,)


@app.cell
def _():
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
        start=0,
        stop=1100,
        step=1,
        value=[0, 365],
        show_value=True,
        label="shift [days]",
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
        start=0,
        step=0.01,
        value=model.fit().finalSettlement,
        label="final settlement [m]",
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
        stop=10000,
        step=1,
        value=900,
        label="End date of the predicted settlement [days]",
    )
    end_time_delta
    return (end_time_delta,)


@app.cell
def _(mo):
    residual_settlement = mo.ui.number(
        start=0,
        step=0.01,
        value=0.1,
        label="Residual settlement [m]",
    )
    residual_settlement
    return (residual_settlement,)


@app.cell
def _(df_measurements, mo, model, np, pd, series, shift, start_date_time):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    days = np.arange(0, 10000 + 1, step=10, dtype=int) + shift.value
    result = model.predict(days)

    df_settlements_predictions = pd.DataFrame(
        {
            "days": days,
            "predict": np.array(result.settlement) * -1,
        }
    )
    df_settlements_predictions["date_time"] = pd.to_timedelta(
        df_settlements_predictions["days"], unit="day"
    ) + pd.to_datetime(start_date_time.value)
    df_settlements_predictions["days"] = (
        df_settlements_predictions["date_time"] - df_measurements["date_time"].min()
    ).dt.days
    return df_settlements_predictions, result


@app.cell
def _(end_time_delta, mo, np, result, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    _settlement = result.settlement_at_day(end_time_delta.value).round(3)
    end_time_settlement = mo.md(
        f"Settlement after {end_time_delta.value} days is {_settlement} meters.",
    )
    end_time_settlement
    return


@app.cell
def _(
    datetime,
    end_time_delta,
    mo,
    np,
    residual_settlement,
    result,
    series,
    start_date_time,
):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    _days = result.release_date(z=residual_settlement.value, day=end_time_delta.value)
    _daytime = start_date_time.value + datetime.timedelta(days=_days)

    release_date = mo.md(
        f"A settlement of {residual_settlement.value} meters is obtaind after {_days} days ({_daytime.strftime('%d/%m/%Y')})",
    )
    release_date
    return


@app.cell
def _(
    alt,
    datetime,
    df_measurements,
    df_settlements_predictions,
    end_time_delta,
    mo,
    np,
    pd,
    series,
    start_date_time,
):
    mo.stop(predicate=all(np.isnan(series.settlements)))

    df_measurements["fill_thicknesses"] = (
        df_measurements["ground_surface_z"].diff().cumsum()
    )
    df_measurements["settlements"] = df_measurements["rod_bottom_z"].diff().cumsum()
    df_measurements["days"] = (
        df_measurements["date_time"] - df_measurements["date_time"].min()
    ).dt.days

    _chart_1 = (
        alt.Chart(df_measurements)
        .mark_line(
            color="orange",
        )
        .encode(
            x=alt.X(
                field="days",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            y=alt.Y(field="settlements", type="quantitative", title="Measurements [m]"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(
                    field="settlements", format=",.2f", title="SettlementElevation"
                ),
                alt.Tooltip(field="rod_bottom_z", format=",.2f", title="Settlement"),
            ],
        )
    )

    _chart_2 = (
        alt.Chart(df_measurements)
        .mark_line(
            color="blue",
        )
        .encode(
            x=alt.X(
                field="days",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            y=alt.Y(
                field="fill_thicknesses",
                type="quantitative",
                title="Measurements [m]",
            ),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(
                    field="fill_thicknesses",
                    format=",.2f",
                    title="SurfaceElevation",
                ),
                alt.Tooltip(
                    field="ground_surface_z", format=",.2f", title="SurfaceLevel"
                ),
            ],
        )
    )

    _chart_3 = (
        alt.Chart(df_settlements_predictions)
        .mark_line(
            color="green",
        )
        .encode(
            x=alt.X(
                field="days",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            y=alt.Y(field="predict", type="quantitative", title="Measurements [m]"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(field="predict", format=",.2f", title="Value"),
            ],
        )
    )

    _rules_1 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "days": [
                        (
                            pd.to_datetime(
                                start_date_time.value
                                + datetime.timedelta(days=end_time_delta.value)
                            ).date()
                            - df_measurements["date_time"].min().date()
                        ).days
                    ],
                    "color": ["black"],
                }
            )
        )
        .mark_rule()
        .encode(
            x=alt.X(
                field="days",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            color=alt.Color("color:N", scale=None),
        )
    )

    _rules_2 = (
        alt.Chart(
            pd.DataFrame(
                {
                    "days": [
                        (
                            pd.to_datetime(start_date_time.value).date()
                            - df_measurements["date_time"].min().date()
                        ).days
                    ],
                    "color": ["black"],
                }
            )
        )
        .mark_rule()
        .encode(
            x=alt.X(
                field="days",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            color=alt.Color("color:N", scale=None),
        )
    )

    (_chart_1 + _chart_2 + _chart_3 + _rules_1 + _rules_2).resolve_scale().properties(
        width=1100,  # Set your desired width here
        height=300,  # Set your desired height here
    )
    return


@app.cell
def _(df_settlements_predictions, mo, np, series):
    mo.stop(predicate=all(np.isnan(series.settlements)))
    csv_download_lazy_prediction = mo.download(
        data=df_settlements_predictions.to_csv(sep=";").encode("utf-8"),
        filename="measurements.csv",
        mimetype="text/csv",
        label="Download CSV",
    )
    csv_download_lazy_prediction
    return


if __name__ == "__main__":
    app.run()
