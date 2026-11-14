FROM python:3.12-slim
COPY requirements.txt /lab/
RUN pip install --no-cache-dir -r /lab/requirements.txt
WORKDIR /lab
COPY retry.py dep.py api.py loadgen.py auditor.py ./
