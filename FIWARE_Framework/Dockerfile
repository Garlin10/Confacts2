FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./app /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt