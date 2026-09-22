# Use a lightweight Python image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your project files
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Run the Uvicorn server
CMD ["uvicorn", "main:fastapi_app", "--host", "0.0.0.0", "--port", "8000"]