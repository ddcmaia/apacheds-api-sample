FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_RUN_PORT=5034
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0"]
