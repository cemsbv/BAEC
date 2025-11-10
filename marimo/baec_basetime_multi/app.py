import marimo

__generated_with = "0.14.17"
app = marimo.App(
    width="medium",
    app_title="BAEC",
    layout_file="layouts/app.grid.json",
)


@app.cell
def _():
    import datetime
    import os
    import sys

    import altair as alt
    import geopandas as gpd
    import leafmap.foliumap as leafmap
    import micropip
    import numpy as np
    import pandas as pd
    import shapely as shp

    import marimo as mo

    return alt, datetime, gpd, leafmap, micropip, mo, np, os, pd, shp, sys


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
    rod_id = mo.ui.multiselect(
        options=_options,
        value=[_options[0]],
        label="Settlement rod",
    )
    rod_id
    return (rod_id,)


@app.cell
def _(manage_project, mo, np, pd, project, rod_id):
    measurements_list = []
    _measurements_db_list = []
    _records = []
    for _id in mo.status.progress_bar(
        rod_id.value,
        title="Loading",
        subtitle="Please wait",
        show_eta=True,
        show_rate=True,
    ):
        # create settlement rod measurement series from BaseTime Bucket
        _series = manage_project.make_settlement_rod_measurement_series(
            project=project.value, rod_id=_id
        )
        _series_df = _series.to_dataframe()

        _records.append(
            {
                "SettlementRod": _id,
                "x": _series_df["rod_top_x"].iloc[-1],
                "y": _series_df["rod_top_y"].iloc[-1],
                "Time;min": _series_df["date_time"].iloc[0],
                "Time;max": _series_df["date_time"].iloc[-1],
                "Duration": (
                    _series_df["date_time"].iloc[-1] - _series_df["date_time"].iloc[0]
                ).days,
                "Number of measurements": len(_series_df),
                "SurfaceLevel;max": _series_df["ground_surface_z"].iloc[-1],
                "SurfaceElevation;max": _series_df["ground_surface_z"].iloc[-1]
                - _series_df["ground_surface_z"].iloc[0],
                "Settlement;max": _series_df["rod_bottom_z"].iloc[-1],
                "SettlementElevation;max": _series_df["rod_bottom_z"].iloc[-1]
                - _series_df["rod_bottom_z"].iloc[0],
            }
        )

        _series_df = _series_df.set_index("date_time", drop=False)
        _series_df = _series_df.resample("1W").max()

        if not all(np.isnan(_series_df["rod_bottom_z"])):
            measurements_list.append(_series)
            _measurements_db_list.append(_series_df)
        else:
            print(f":warning: No measurements for {_id}")

    measurements_db = pd.concat(_measurements_db_list)
    measurements_df = pd.DataFrame(_records)
    return measurements_db, measurements_list


@app.cell
def _(gpd, measurements_db, shp):
    measurements_db["geometry"] = measurements_db[["rod_top_x", "rod_top_y"]].apply(
        lambda x: shp.Point(*x), axis=1
    )
    measurements_gdf = gpd.GeoDataFrame(
        measurements_db, geometry="geometry", crs="epsg:28992"
    ).to_crs("WGS84")
    return (measurements_gdf,)


@app.cell
def _(leafmap, measurements_gdf):
    m = leafmap.Map(
        tiles="CartoDB Positron",
        measure_control=False,
        draw_control=False,
        center=(52.4, 4.9),
        zoom=9,
    )
    m.add_gdf(measurements_gdf, layer_name="Measurements")
    m
    return


@app.cell
def _(measurements_db, mo):
    start_date_time = mo.ui.date.from_series(
        measurements_db["date_time"], label="Start date"
    )
    start_date_time
    return (start_date_time,)


@app.cell
def _(alt, measurements_db, pd, start_date_time):
    _chart_1 = (
        alt.Chart(measurements_db)
        .mark_line()
        .encode(
            x=alt.X(
                field="date_time",
                type="temporal",
                timeUnit="yearmonthdate",
                title="Date",
            ),
            y=alt.Y(
                field="ground_surface_z",
                type="quantitative",
                title="Measurements [m NAP]",
            ),
            color=alt.Color(field="object_id", type="nominal", title="Legend"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(field="ground_surface_z", format=",.2f", title="Value"),
                alt.Tooltip(field="object_id"),
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
def _(alt, measurements_db, pd, start_date_time):
    _chart_1 = (
        alt.Chart(measurements_db)
        .mark_line()
        .encode(
            x=alt.X(
                field="date_time",
                type="temporal",
                timeUnit="yearmonthdate",
                title="Date",
            ),
            y=alt.Y(
                field="rod_bottom_z",
                type="quantitative",
                title="Measurements [m NAP]",
            ),
            color=alt.Color(field="object_id", type="nominal", title="Legend"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(field="rod_bottom_z", format=",.2f", title="Value"),
                alt.Tooltip(field="object_id"),
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
def _(measurements_db, mo):
    csv_download_lazy_measurements = mo.download(
        data=measurements_db.to_csv(sep=";").encode("utf-8"),
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
    measurements_list,
    mo,
    start_date_time,
):
    series_list = []
    for measurement in mo.status.progress_bar(
        measurements_list,
        title="Loading",
        subtitle="Please wait",
        show_eta=True,
        show_rate=True,
    ):
        try:
            _series = MeasuredSettlementSeries(
                measurement,
                start_date_time=datetime.datetime.combine(
                    start_date_time.value,
                    measurement.to_dataframe()["date_time"].min().time(),
                ),
            )

            series_list.append(_series)
        except ValueError as e:
            print(
                f":warning: {measurement.object_id} provided the following error: {e}"
            )
    return measurement, series_list


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
        stop=10,
        step=1,
        value=[0, 6],
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
    measurement,
    mo,
    primary_settlement_bounds,
    series_list,
    shift_bounds,
):
    mo.stop(predicate=len(series_list) == 0)
    params = FitCoreParameters(
        primarySettlement=FitCoreParametersBounds(*primary_settlement_bounds.value),
        shift=FitCoreParametersBounds(*shift_bounds.value),
        hydrodynamicPeriod=FitCoreParametersBounds(*hydrodynamic_period_bounds.value),
        finalSettlement=FitCoreParametersBounds(*final_settlement_bounds.value),
    )

    model_list = []
    for _series in mo.status.progress_bar(
        series_list,
        title="Loading",
        subtitle="Please wait",
        show_eta=True,
        show_rate=True,
    ):
        try:
            _model = FitCoreModelGenerator(
                series=_series, client=client, model_parameters=params
            )

            model_list.append(_model)
        except ValueError as e:
            print(
                f":warning: {measurement.object_id} provided the following error: {e}"
            )
    return (model_list,)


@app.cell
def _(datetime, measurement, mo, model_list, np, pd, start_date_time):
    mo.stop(predicate=len(model_list) == 0)

    prediction_db_list = []
    _records = []
    for _model in mo.status.progress_bar(
        model_list,
        title="Loading",
        subtitle="Please wait",
        show_eta=True,
        show_rate=True,
    ):
        try:
            days = (
                np.logspace(start=0, stop=5, endpoint=True, num=100, dtype=np.int64)
                + _model.model.shift
            )
            result = _model.predict(days)

            _records.append(
                {
                    "SettlementRod": _model.series.series.object_id,
                    "HydrodynamicPeriod": _model.model.hydrodynamicPeriod,
                    "PrimarySettlement": _model.model.primarySettlement,
                    "Shift": _model.model.shift,
                    "FinalSettlement": _model.model.finalSettlement,
                }
            )

            _df_left = pd.DataFrame(
                {
                    "days": _model.series.days,
                    "fill_thicknesses": _model.series.fill_thicknesses,
                    "settlements": np.array(_model.series.settlements) * -1,
                    "merge": (np.round(_model.series.days, 3) * 100).astype(int),
                }
            )

            _df_right = pd.DataFrame(
                {
                    "days": days,
                    "predict": np.array(result.settlement) * -1,
                    "merge": (np.round(days, 3) * 100).astype(int),
                }
            )

            _df = pd.merge(_df_right, _df_left, on="merge", how="left")

            _df["days_merge"] = (_df["merge"] / 100).astype(int)
            _df["date_time"] = pd.to_datetime(
                [
                    datetime.timedelta(days=days) + start_date_time.value
                    for days in _df["days_merge"]
                ],
                errors="coerce",
            )
            _df = _df.interpolate(limit_direction="backward")
            _df["object_id"] = _model.series.series.object_id
            prediction_db_list.append(_df)
        except ValueError as e:
            print(
                f":warning: {measurement.object_id} provided the following error: {e}"
            )

    prediction_db = pd.concat(prediction_db_list)
    prediction_df = pd.DataFrame(_records)
    return prediction_db, prediction_df


@app.cell
def _(prediction_df):
    prediction_df
    return


@app.cell
def _(alt, mo, model_list, prediction_db):
    mo.stop(predicate=len(model_list) == 0)

    _chart_1 = (
        alt.Chart(prediction_db)
        .mark_line()
        .encode(
            x=alt.X(
                field="days_merge",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            y=alt.Y(
                field="fill_thicknesses",
                type="quantitative",
                title="Measurements [m]",
            ),
            color=alt.Color(field="object_id", type="nominal", title="Legend"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(field="fill_thicknesses", format=",.2f", title="Value"),
                alt.Tooltip(field="object_id"),
            ],
        )
    )

    (_chart_1).resolve_scale()
    return


@app.cell
def _(alt, mo, model_list, prediction_db):
    mo.stop(predicate=len(model_list) == 0)
    _colors = alt.Scale(domain=["settlements", "predict"], range=["orange", "green"])

    _chart_1 = (
        alt.Chart(prediction_db)
        .mark_line()
        .encode(
            x=alt.X(
                field="days_merge",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            y=alt.Y(field="predict", type="quantitative", title="Measurements [m]"),
            color=alt.Color(field="object_id", type="nominal", title="Legend"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(field="predict", format=",.2f", title="Value"),
                alt.Tooltip(field="object_id"),
            ],
        )
    )
    _chart_2 = (
        alt.Chart(prediction_db)
        .mark_line()
        .encode(
            x=alt.X(
                field="days_merge",
                type="quantitative",
                title="Days",
                scale=alt.Scale(type="symlog"),
            ),
            y=alt.Y(field="settlements", type="quantitative", title="Measurements [m]"),
            color=alt.Color(field="object_id", type="nominal", title="Legend"),
            tooltip=[
                alt.Tooltip(field="date_time", timeUnit="yearmonthdate", title="Date"),
                alt.Tooltip(field="settlements", format=",.2f", title="Value"),
                alt.Tooltip(field="object_id"),
            ],
        )
    )

    (_chart_1 + _chart_2).resolve_scale()
    return


@app.cell
def _(mo, model_list, prediction_db):
    mo.stop(predicate=len(model_list) == 0)
    csv_download_lazy_prediction = mo.download(
        data=prediction_db.to_csv(sep=";").encode("utf-8"),
        filename="measurements.csv",
        mimetype="text/csv",
        label="Download CSV",
    )
    csv_download_lazy_prediction
    return


if __name__ == "__main__":
    app.run()
