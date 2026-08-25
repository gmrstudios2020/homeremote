FROM python:3.13-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg pulseaudio-utils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py /app/app.py
COPY templates /app/templates
ENV PYTHONUNBUFFERED=1
ENV PULSE_SERVER=unix:/var/run/pulse/native
EXPOSE 8089
CMD ["python", "/app/app.py"]
