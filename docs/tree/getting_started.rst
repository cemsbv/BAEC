Getting started
===============

The easiest way to get started with `baec` is in the **Jupyter Notebook**.

Installation
------------
To install this package, including the `basetime` reading functionality, run:

.. code-block::

    pip install baec[aws]


To skip the installation of the optional library, in case you do not need it
(e.g. not connecting to the aws server), run:

.. code-block::

    pip install baec

Than you can import `baec` as follows:

.. ipython:: python

    import os

    import matplotlib.pyplot as plt
    import pandas as pd

    from baec.measurements.io.zbase import measurements_from_zbase

or any equivalent :code:`import` statement.

SettlementRodMeasurementSeries
--------------------------------

The first thing to do is to create `SettlementRodMeasurementSeries` classes.
This class holds the information of a selection of `Measurements`.

For more information on the :func:`baec.measurements.settlement_rod_measurement_series
.SettlementRodMeasurementSeries` class go the the reference.


.. ipython:: python

    root = os.environ["DOC_PATH"]
    filepath = os.path.join(root, "_static/data/E790M.csv")

    # Create series from zbase csv file
    measurements = measurements_from_zbase(
        filepath_or_buffer=filepath, project_name="Docs"
    )

    # plot measurements
    @savefig measurements.png
    measurements.plot_z_time()


MeasuredSettlementSeries
--------------------------------

The next step is to transform the `SettlementRodMeasurementSeries` to a `MeasuredSettlementSeries`.
Based on the start date the displacements are calculated.

For more information on the :func:`baec.measurements.measured_settlement_series.MeasuredSettlementSeries`
class go the the reference.


.. ipython:: python

    import datetime

    from baec.measurements.measured_settlement_series import MeasuredSettlementSeries

    # Create series from measurements
    series = MeasuredSettlementSeries(
        measurements,
        start_date_time=measurements.measurements[0].date_time
        + datetime.timedelta(days=200),
    )

    # plot displacements
    @savefig displacements.png
    series.plot_xy_displacements_plan_view()
