FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mavlink_sim.py .

RUN useradd --create-home --uid 10001 sim
USER sim

CMD ["python", "mavlink_sim.py"]
