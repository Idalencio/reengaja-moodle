FROM python:3.12-slim
WORKDIR /app
COPY demo ./demo
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "demo.moodle_server"]
