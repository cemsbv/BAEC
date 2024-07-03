from __future__ import annotations

import datetime
from typing import Type

import pytest
from matplotlib import pyplot as plt

from baec.measurements.measured_settlement_series import MeasuredSettlementSeries
from baec.measurements.settlement_rod_measurement_series import (
    SettlementRodMeasurementSeries,
)


@pytest.mark.parametrize(
    "start_index,start_date_time,expected_start_index",
    [
        (None, None, 0),  # default start index and start date time
        (5, None, 5),
        (-2, None, -2),
        (None, datetime.datetime(2024, 4, 11, 0, 0, 0), 2),
        (None, datetime.datetime(2024, 4, 11, 4, 0, 0), 3),
    ],
)
def test_measured_settlement_series_init_with_valid_input(
    example_settlement_rod_measurement_series: SettlementRodMeasurementSeries,
    start_index: int,
    start_date_time: datetime.datetime,
    expected_start_index: int,
) -> None:
    """Test initialization method of MeasuredSettlementSeries with valid input."""
    measurement_series = example_settlement_rod_measurement_series

    # Create series
    if start_index is None and start_date_time is None:
        series = MeasuredSettlementSeries(
            series=measurement_series,
        )
    else:
        series = MeasuredSettlementSeries(
            series=measurement_series,
            start_index=start_index,
            start_date_time=start_date_time,
        )

    assert isinstance(series, MeasuredSettlementSeries)
    assert series.project == measurement_series.project
    assert series.object_id == measurement_series.object_id
    assert (
        series.coordinate_reference_systems.horizontal_units
        == measurement_series.coordinate_reference_systems.horizontal_units
    )
    assert (
        series.coordinate_reference_systems.vertical_units
        == measurement_series.coordinate_reference_systems.vertical_units
    )

    df = measurement_series.to_dataframe()

    idx = expected_start_index  # expected start index
    assert len(series.items) == len(df.iloc[idx:])
    assert series.start_date_time == measurement_series.measurements[idx].date_time
    assert series.date_times == df["date_time"].to_list()[idx:]
    assert series.days == list(
        [
            (d - series.start_date_time).total_seconds() / 86400.0
            for d in df["date_time"].to_list()[idx:]
        ]
    )
    assert (
        series.fill_thicknesses
        == (df["ground_surface_z"] - df["rod_bottom_z"]).to_list()[idx:]
    )
    assert (
        series.settlements
        == (df["rod_bottom_z"].iloc[idx] - df["rod_bottom_z"].iloc[idx:]).to_list()
    )
    assert (
        series.x_displacements
        == (df["rod_top_x"].iloc[idx:] - df["rod_top_x"].iloc[idx]).to_list()
    )
    assert (
        series.y_displacements
        == (df["rod_top_y"].iloc[idx:] - df["rod_top_y"].iloc[idx]).to_list()
    )


def test_measured_settlement_series_with_invalid_input(
    example_settlement_rod_measurement_series: SettlementRodMeasurementSeries,
) -> None:
    """Test initialization method of MeasuredSettlementSeries with invalid input."""

    measurement_series = example_settlement_rod_measurement_series

    # Invalid series: None
    with pytest.raises(TypeError, match="series"):
        MeasuredSettlementSeries(
            series=None,
        )

    # Invalid start_index: float
    with pytest.raises(TypeError, match="start_index"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_index=5.0,
        )

    # Invalid start_index: out of range with positive value
    with pytest.raises(IndexError, match="start_index"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_index=20,
        )

    # Invalid start_index: out of range with negative value
    with pytest.raises(IndexError, match="start_index"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_index=-20,
        )

    # Invalid start_date_time: str
    with pytest.raises(TypeError, match="start_date_time"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_date_time="2024-04-11 00:00:00",
        )

    # Invalid start_date_time: out of range with date before series
    with pytest.raises(ValueError, match="start_date_time"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_date_time=datetime.datetime(2024, 4, 1, 0, 0, 0),
        )

    # Invalid start_date_time: out of range with date after series
    with pytest.raises(ValueError, match="start_date_time"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_date_time=datetime.datetime(2024, 4, 20, 0, 0, 0),
        )

    # Both start_index and start_date_time can be provided.
    with pytest.raises(ValueError, match="'start_index' or 'start_date_time'"):
        MeasuredSettlementSeries(
            series=measurement_series,
            start_index=5,
            start_date_time=datetime.datetime(2024, 4, 11, 0, 0, 0),
        )


@pytest.mark.parametrize(
    "start_index,expected_start_index_or_error",
    [
        (0, 0),
        (5, 5),
        (-2, -2),
        (5.0, TypeError),
        (20, IndexError),  # out of range with positive value
        (-20, IndexError),  # out of range with negative value
    ],
)
def test_measured_settlement_series_start_index_setter(
    example_settlement_rod_measurement_series: SettlementRodMeasurementSeries,
    start_index: int,
    expected_start_index_or_error: int | Type[Exception],
) -> None:
    """Test the start_index setter method of MeasuredSettlementSeries."""

    # Create the series
    measurement_series = example_settlement_rod_measurement_series

    series = MeasuredSettlementSeries(
        series=measurement_series,
    )

    # Set the start_index and check whether the expected error is
    # raised or the expected output is obtained.
    if isinstance(expected_start_index_or_error, Exception):
        with pytest.raises(expected_start_index_or_error):
            series.start_index = start_index

    elif isinstance(expected_start_index_or_error, int):
        series.start_index = start_index

        # Check the output
        df = measurement_series.to_dataframe()
        idx = expected_start_index_or_error
        assert len(series.items) == len(df.iloc[idx:])
        assert series.start_date_time == measurement_series.measurements[idx].date_time
        assert series.date_times == df["date_time"].to_list()[idx:]
        assert series.days == list(
            [
                (d - series.start_date_time).total_seconds() / 86400.0
                for d in df["date_time"].to_list()[idx:]
            ]
        )
        assert (
            series.fill_thicknesses
            == (df["ground_surface_z"] - df["rod_bottom_z"]).to_list()[idx:]
        )
        assert (
            series.settlements
            == (df["rod_bottom_z"].iloc[idx] - df["rod_bottom_z"].iloc[idx:]).to_list()
        )
        assert (
            series.x_displacements
            == (df["rod_top_x"].iloc[idx:] - df["rod_top_x"].iloc[idx]).to_list()
        )
        assert (
            series.y_displacements
            == (df["rod_top_y"].iloc[idx:] - df["rod_top_y"].iloc[idx]).to_list()
        )


@pytest.mark.parametrize(
    "start_date_time,expected_start_index_or_error",
    [
        (datetime.datetime(2024, 4, 11, 0, 0, 0), 2),
        (datetime.datetime(2024, 4, 11, 4, 0, 0), 3),
        ("2024-04-11 00:00:00", TypeError),
        (datetime.datetime(2024, 4, 1, 0, 0, 0), ValueError),  # date before series
    ],
)
def test_measured_settlement_series_start_datetime_setter(
    example_settlement_rod_measurement_series: SettlementRodMeasurementSeries,
    start_date_time: datetime.datetime,
    expected_start_index_or_error: int | Type[Exception],
) -> None:
    """Test the start_datetime setter method of MeasuredSettlementSeries."""

    # Create the series
    measurement_series = example_settlement_rod_measurement_series

    series = MeasuredSettlementSeries(
        series=measurement_series,
    )

    # Set the start_datetime and check whether the expected error is
    # raised or the expected output is obtained.
    if isinstance(expected_start_index_or_error, Exception):
        with pytest.raises(expected_start_index_or_error):
            series.start_date_time = start_date_time

    elif isinstance(expected_start_index_or_error, int):
        series.start_date_time = start_date_time

        # Check the output
        df = measurement_series.to_dataframe()
        idx = expected_start_index_or_error
        assert len(series.items) == len(df.iloc[idx:])
        assert series.start_date_time == measurement_series.measurements[idx].date_time
        assert series.date_times == df["date_time"].to_list()[idx:]
        assert series.days == list(
            [
                (d - series.start_date_time).total_seconds() / 86400.0
                for d in df["date_time"].to_list()[idx:]
            ]
        )
        assert (
            series.fill_thicknesses
            == (df["ground_surface_z"] - df["rod_bottom_z"]).to_list()[idx:]
        )
        assert (
            series.settlements
            == (df["rod_bottom_z"].iloc[idx] - df["rod_bottom_z"].iloc[idx:]).to_list()
        )
        assert (
            series.x_displacements
            == (df["rod_top_x"].iloc[idx:] - df["rod_top_x"].iloc[idx]).to_list()
        )
        assert (
            series.y_displacements
            == (df["rod_top_y"].iloc[idx:] - df["rod_top_y"].iloc[idx]).to_list()
        )


def test_days_to_date_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test days_to_date_time method"""

    series = example_measured_settlement_series

    # 1. Test with valid input
    assert series.days_to_date_time(days=15) == datetime.datetime(2024, 4, 24, 0, 0, 0)
    assert series.days_to_date_time(days=15.25) == datetime.datetime(
        2024, 4, 24, 6, 0, 0
    )
    assert series.days_to_date_time(days=-3) == datetime.datetime(2024, 4, 6, 0, 0, 0)

    series._start_date_time = datetime.datetime(2024, 4, 24, 4, 0, 0)
    assert series.days_to_date_time(days=7) == datetime.datetime(2024, 5, 1, 4, 0, 0)

    # 2. Test with invalid input: str
    with pytest.raises(TypeError, match="days"):
        series.days_to_date_time(days="5")


def test_date_time_to_days(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test date_time_to_days method"""

    series = example_measured_settlement_series

    # 1. Test with valid input
    assert (
        series.date_time_to_days(date_time=datetime.datetime(2024, 4, 24, 0, 0, 0))
        == 15
    )
    assert (
        series.date_time_to_days(date_time=datetime.datetime(2024, 4, 24, 6, 0, 0))
        == 15.25
    )
    assert (
        series.date_time_to_days(date_time=datetime.datetime(2024, 4, 6, 0, 0, 0)) == -3
    )

    series._start_date_time = datetime.datetime(2024, 4, 24, 4, 0, 0)
    assert (
        series.date_time_to_days(date_time=datetime.datetime(2024, 5, 1, 4, 0, 0)) == 7
    )

    # 2. Test with invalid input: str
    with pytest.raises(TypeError, match="date_time"):
        series.date_time_to_days(date_time="2024-04-24 00:00:00")


def test_measured_settlement_series_to_dataframe_method(
    example_settlement_rod_measurement_series: SettlementRodMeasurementSeries,
) -> None:
    """Test the to_dataframe method of MeasuredSettlementSeries."""
    measurement_series = example_settlement_rod_measurement_series

    # Valid input with default start_index and start_date_time.
    series = MeasuredSettlementSeries(
        series=measurement_series,
    )

    df = series.to_dataframe()

    # Check that the DataFrame has the correct number of rows.
    assert len(df) == len(measurement_series.measurements)

    # Check that the DataFrame has the correct data.
    for i, item in enumerate(series.items):
        assert df.iloc[i]["project_id"] == item.project.id
        assert df.iloc[i]["project_name"] == item.project.name
        assert df.iloc[i]["object_id"] == item.object_id
        assert df.iloc[i]["start_date_time"] == item.start_date_time
        assert df.iloc[i]["date_time"] == item.date_time
        assert df.iloc[i]["days"] == item.days
        assert df.iloc[i]["fill_thickness"] == item.fill_thickness
        assert df.iloc[i]["settlement"] == item.settlement
        assert df.iloc[i]["x_displacement"] == item.x_displacement
        assert df.iloc[i]["y_displacement"] == item.y_displacement
        assert df.iloc[i]["horizontal_units"] == item.horizontal_units
        assert df.iloc[i]["vertical_units"] == item.vertical_units
        assert df.iloc[i]["status"] == item.status.value
        assert df.iloc[i]["status_messages"] == "(code=0, description=OK, level=OK)"


def test_plot_x_displacement_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_x_displacement_time method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    ax = series.plot_x_displacement_time()

    # 2. Plot giving axes
    _, ax = plt.subplots()
    assert ax == series.plot_x_displacement_time(axes=ax)

    # 3. Plot with log_time = False
    series.plot_x_displacement_time(log_time=False)

    # 4. Plot with min_log_time = 2.0
    series.plot_x_displacement_time(min_log_time=2.0)

    # 5. Plot with add_date_time = False
    series.plot_x_displacement_time(add_date_time=False)

    # 6. Plot with datetime_format = "%Y-%m-%d"
    series.plot_x_displacement_time(datetime_format="%Y-%m-%d")

    # Show the plots
    if show:
        plt.show()

    plt.close("all")


def test_plot_y_displacement_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_y_displacement_time method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    ax = series.plot_y_displacement_time()

    # 2. Plot giving axes
    _, ax = plt.subplots()
    assert ax == series.plot_y_displacement_time(axes=ax)

    # 3. Plot with log_time = False
    series.plot_y_displacement_time(log_time=False)

    # 4. Plot with min_log_time = 2.0
    series.plot_y_displacement_time(min_log_time=2.0)

    # 5. Plot with add_date_time = False
    series.plot_y_displacement_time(add_date_time=False)

    # 6. Plot with datetime_format = "%Y-%m-%d"
    series.plot_y_displacement_time(datetime_format="%Y-%m-%d")

    # Show the plots
    if show:
        plt.show()

    plt.close("all")


def test_plot_settlement_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_settlement_time method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    ax = series.plot_settlement_time()

    # 2. Plot giving axes
    _, ax = plt.subplots()
    assert ax == series.plot_settlement_time(axes=ax)

    # 3. Plot with log_time = False
    series.plot_settlement_time(log_time=False)

    # 4. Plot with min_log_time = 2.0
    series.plot_settlement_time(min_log_time=2.0)

    # 5. Plot with add_date_time = False
    series.plot_settlement_time(add_date_time=False)

    # 6. Plot with datetime_format = "%Y-%m-%d"
    series.plot_settlement_time(datetime_format="%Y-%m-%d")

    # Show the plots
    if show:
        plt.show()

    plt.close("all")


def test_plot_fill_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_fill_time method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    ax = series.plot_fill_time()

    # 2. Plot giving axes
    _, ax = plt.subplots()
    assert ax == series.plot_fill_time(axes=ax)

    # 3. Plot with log_time = False
    series.plot_fill_time(log_time=False)

    # 4. Plot with min_log_time = 2.0
    series.plot_fill_time(min_log_time=2.0)

    # 5. Plot with add_date_time = False
    series.plot_fill_time(add_date_time=False)

    # 6. Plot with datetime_format = "%Y-%m-%d"
    series.plot_fill_time(datetime_format="%Y-%m-%d")

    # Show the plots
    if show:
        plt.show()

    plt.close("all")


def test_plot_fill_settlement_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_fill_settlement_time method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    series.plot_fill_settlement_time()

    # 2. Plot with log_time = False
    series.plot_fill_settlement_time(log_time=False)

    # 3. Plot with min_log_time = 2.0
    series.plot_fill_settlement_time(min_log_time=2.0)

    # 4. Plot with add_date_time = False
    series.plot_fill_settlement_time(add_date_time=False)

    # 5. Plot with datetime_format = "%Y-%m-%d"
    series.plot_fill_settlement_time(datetime_format="%Y-%m-%d")

    # Show the plots
    if show:
        plt.show()

    plt.close("all")


def test_plot_displacements_time(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_displacements_time method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    series.plot_displacements_time()

    # 2. Plot with log_time = False
    series.plot_displacements_time(log_time=False)

    # 3. Plot with min_log_time = 2.0
    series.plot_displacements_time(min_log_time=2.0)

    # 4. Plot with add_date_time = False
    series.plot_displacements_time(add_date_time=False)

    # 5. Plot with datetime_format = "%Y-%m-%d"
    series.plot_displacements_time(datetime_format="%Y-%m-%d")

    # Show the plots
    if show:
        plt.show()

    plt.close("all")


def test_plot_xy_displacements_plan_view(
    example_measured_settlement_series: MeasuredSettlementSeries,
) -> None:
    """Test plot_xy_displacements_plan_view method are generated without error."""

    show = False

    series = example_measured_settlement_series

    # 1. Plot without giving axes
    ax = series.plot_xy_displacements_plan_view()

    # 2. Plot giving axes
    _, ax = plt.subplots()
    assert ax == series.plot_xy_displacements_plan_view(axes=ax)

    # Show the plots
    if show:
        plt.show()

    plt.close("all")
