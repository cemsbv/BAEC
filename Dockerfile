# save to file with `docker save baec_app > baec_app.tar`
#
# syntax=docker/dockerfile:1.4

# Choose a python version that you know works with your application
FROM python:3.13-slim-trixie

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

# Set the working directory
WORKDIR /app

# Copy requirements file
COPY --link requirements.txt .

# Install the requirements using uv
RUN uv pip install -r requirements.txt

# Copy application files
COPY --link ./marimo/baec_basetime_multi/app.py .
COPY --link ./marimo/baec_basetime_multi/layouts/* ./layouts/
COPY --link ./src/baec/* .baec/

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
CMD [ "marimo", "run", "app.py", "--host", "0.0.0.0", "-p", "8080" ]