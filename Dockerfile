# docker build -t baec_standalone:latest .
# docker save baec_standalone:latest -o baec_standalone_run.tar
# docker load -i baec_standalone_run.tar
#
# syntax=docker/dockerfile:1.4

# Choose a python version that you know works with your application
FROM python:3.14-slim-trixie

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

# Set the working directory
WORKDIR /app

# Copy requirements file and local module
COPY requirements.txt /app/
COPY ./src/baec/ /app/src/baec/
COPY pyproject.toml /app/

# Install the requirements using uv
RUN uv pip install --no-cache-dir -r requirements.txt
RUN uv pip install --no-cache-dir /app/.

# remove local modul after installation
RUN rm -rf /app/src

# Copy application files
COPY ./marimo/baec_basetime_multi/app.py .
COPY ./marimo/baec_basetime_multi/layouts/* ./layouts/

# Expose port 8080 for the application
EXPOSE 8080

# Create a non-root user and switch to it
RUN useradd -m app_user
RUN chown -R app_user:app_user /app
RUN chmod 755 /app
USER app_user

# Docker Health Check
HEALTHCHECK CMD curl --fail http://localhost:8080 || exit 1

# After container starts, run the marimo application
CMD [ "marimo", "edit", "app.py", "--host", "0.0.0.0", "-p", "8080", "--token-password", "sup3rs3cr3t" ]