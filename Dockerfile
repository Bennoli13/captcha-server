FROM python

WORKDIR /app

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/Bennoli13/captcha-server .

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]
