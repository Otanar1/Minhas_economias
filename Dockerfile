FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Verificar se o arquivo main.py existe
RUN ls -la src/

CMD ["python", "src/main.py"]
