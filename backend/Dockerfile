
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set the working directory in the container
WORKDIR /app

# Copy the project files
COPY pyproject.toml .
# Create a virtual environment and install dependencies
RUN uv venv && uv pip install -r pyproject.toml

# Copy the rest of the application
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application using the virtual environment created by uv
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

