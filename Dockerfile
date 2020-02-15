FROM python:2
WORKDIR /usr/src/app
COPY requirements.txt ./
COPY ecoforest-proxy.py ./
RUN pip install --no-cache-dir -r requirements.txt
HEALTHCHECK CMD curl --fail http://localhost:8998/healthcheck || exit 1
CMD [ "python", "./ecoforest-proxy.py" ]
