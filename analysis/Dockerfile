FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install setuptools wheel --break-system-packages
RUN pip install -r requirements.txt --break-system-packages

COPY . .

CMD ["python", "app.py"]
