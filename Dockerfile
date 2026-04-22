FROM python:3.12-slim
WORKDIR /app
COPY poetry.lock pyproject.toml .
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --only main --no-interaction --no-ansi --no-root
COPY src/booking_app ./booking_app
EXPOSE 8000
CMD ["sh", "-c", "uvicorn booking_app.main:app --host 0.0.0.0 --port $PORT"]