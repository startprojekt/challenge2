FROM python:3.8-slim-buster

ENV DEBUG=1
ENV SECRET_KEY="oXceDVy4ed$*xl@d62u*-0s*$219!g%&lilb7u(dk#do*(hvg_"

# Instal gcc.
RUN apt-get update \
&& apt-get install gcc nodejs npm -y \
&& apt-get clean

# Install Python dependencies.
RUN pip install --upgrade pip
RUN mkdir /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt

WORKDIR /app
COPY . /app/

# Install static dependencies (e.g. "Bootstrap").
RUN cd /app/theme/static/ && npm install

# Entrypoint for Django server.
COPY docker-entrypoint.sh /
ENTRYPOINT ["bash", "/docker-entrypoint.sh"]


