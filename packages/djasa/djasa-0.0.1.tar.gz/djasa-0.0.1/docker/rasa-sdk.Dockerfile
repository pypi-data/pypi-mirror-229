# Extend the official Rasa SDK image
FROM rasa/rasa-sdk:3.6.2

# Change back to root user to install dependencies
USER root

# Install system-level dependencies
RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
 && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements/requirements.txt /app/requirements.txt
RUN pip install django==4.2.5 requests==2.31.0

ENV DJANGO_SETTINGS_MODULE example_project.conf.settings
ENV PYTHONPATH /app:/app/example_project


# Switch back to non-root to run code
USER 1001