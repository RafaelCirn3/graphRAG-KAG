FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY scripts ./scripts
COPY tests ./tests
COPY data ./data
COPY docs ./docs

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "src/ui/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
