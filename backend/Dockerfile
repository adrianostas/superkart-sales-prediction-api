FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies without caching build wheels
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application files (app.py, best_sales_model.pkl, etc.)
COPY . .

# Expose port 7860
EXPOSE 7860

# Run Gunicorn pointing to the Flask instance 'app' inside 'app.py'
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]
