# Changelog

All notable changes to this project will be documented in this file.

## [0.2.2] - 2025-09-02

### Miscellaneous Tasks

#### Marimo

- Install missing dependencies


### Build

#### Marimo

- Uses actions/checkout@v4
- Update notebook path
- Update notebook path
- Set UV_SYSTEM_PYTHON
- Build and deploy marimo app in job
- Build and deploy marimo app in job


### Format

#### CHECKOV

- Set top-level permissions


## [0.2.0] - 2025-08-28

### Bug Fixes

#### Actions

- Resolve github actions

#### Basetime

- Catch errors when parsing data

#### Fitcore

- Raise user friendly error

#### Typo

- Fix typo in pyproject.toml


### Documentation

#### Coveralls

- Update coveralls link


### Features

#### Aws

- Allow to set s3bucket, region and company name

#### Fitcore

- Allow user input for model params

#### Gui

- Update in improve figures and tables
- Add result field to gui

#### Uv

- Migrate from pip-tools to uv


### Miscellaneous Tasks


### Performance

#### Basetime

- Revert changes in collection date, use lambda function


### Styling

#### Format

- Format files with super-linter

#### Mypy

- Exclude notebooks folder from mypy


### Build

#### UI

- Initial setup marimo app

#### Actions

- Allow to use uv in system environment

#### Deps

- Bump super-linter from 7 to 8
- Bump actions/checkout from 4 to 5

#### Docs

- Update ubuntu version


## [0.1.0] - 2024-10-11

### Bug Fixes

#### Plot

- Allow for nan in plot


### Documentation


### Features

#### Baetime

- Initial setup of the BaseTime bucket parser (#31)

#### Example

- Add fitcore to example pipeline

#### Measured_settlement

- Add classes MeasuredSettlement and MeasuredSettlementSeries including plot methods

#### Settlement_rod_measurement

- Add class SettlementRodMeasurement

#### Settlement_rod_measurement_series

- Add SettlementRodMeasurementSeries class to represent a series of measurements for a single settlement rod and update docs


### Miscellaneous Tasks

#### Docs

- Update doc build job


### Refactor

#### Settlement_rod_measurement

- Refactor SettlementRodMeasurement according to comments from Michel (CRUX) and Daniel (BouwRisk)
- Refactor names of some attributes of SettlementRodMeasurement, improving docstrings and adding sphinx docs


### Styling


### Apply

#### #18

- Add note to CoordinateReferenceSystems about NL and modify figure according to PR #18 comments
- Add plots to SettlementRodMeasurementSeries, add CoordinateReferenceSystems class and refactor attribute names in SettlementRodMeasurement as discussed in comments of PR #18


## [0.0.1] - 2024-05-03

<!-- CEMS BV. -->
