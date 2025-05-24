FROM python:3.10

WORKDIR /self-tracker
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
