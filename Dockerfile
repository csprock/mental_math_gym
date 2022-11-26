FROM csprock/python-base:3.10.7-slim-bullseye


COPY requirements.txt /home/user/requirements.txt
RUN pip install -r /home/user/requirements.txt && rm /home/user/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8050

CMD gunicorn -b 0.0.0.0:8050 app:server