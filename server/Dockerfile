FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir hatch

COPY ./sdk /sdk
COPY ./server /app

RUN pip install --no-cache-dir -e /sdk
RUN pip install --no-cache-dir -e /app

EXPOSE 8080

CMD ["uvicorn", "agentspine_server.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
