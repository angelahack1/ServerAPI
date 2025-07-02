FROM python:3.12-slim-bookworm

RUN useradd --create-home appuser
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PORT=5000

WORKDIR /home/appuser/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
RUN chown -R appuser:appuser /home/appuser
USER appuser

EXPOSE $PORT
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "--log-level", "info", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "serverAPI:app"]