FROM python:3.11-slim

WORKDIR /app

RUN pip install hatch

COPY ./sdk /sdk
COPY ./server /app

# Install sdk from local directory
RUN pip install -e /sdk
RUN pip install -e .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
