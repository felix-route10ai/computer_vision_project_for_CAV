FROM python:3.11-slim as builder
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY main.py .
COPY mock_data_generator.py .

# Generate mock data at build time
RUN python mock_data_generator.py

# Cloud Run expects port from $PORT environment variable
ENV PORT=8080
EXPOSE 8080

# Run FastAPI with uvicorn
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}