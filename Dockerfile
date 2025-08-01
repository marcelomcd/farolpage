FROM python:3.10

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . .



EXPOSE 8050

CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server", "--workers", "4", "--timeout", "300"]