FROM python:latest

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y python3-venv

# Copy project files
COPY . .

# Create and activate virtual environment
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir pandas numpy

# Ensure Python uses the venv by updating PATH
ENV PATH="/opt/venv/bin:$PATH"

# Start chatbot application
CMD ["python", "app.py"]
