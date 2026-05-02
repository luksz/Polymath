FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install uv
COPY pyproject.toml .
COPY src/ src/
RUN uv pip install --system .

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /build/src /app/src
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
