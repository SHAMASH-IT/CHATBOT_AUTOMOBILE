# Use the latest Python image
FROM python:latest

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for virtual environments
RUN apt-get update && apt-get install -y python3-venv

# Copy project files
COPY . .

# Create and activate virtual environment
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Ensure Python uses the venv by updating PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose the port that the chatbot runs on
EXPOSE 5000

# Start the chatbot application
CMD ["python", "app.py"]
