FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY infra ./infra
COPY acompanhamento ./acompanhamento
USER 10001:10001
EXPOSE 8081
CMD ["python", "-m", "acompanhamento"]
