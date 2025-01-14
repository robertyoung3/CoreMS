FROM python:3.10-slim

WORKDIR /home/corems

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    mono-complete \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only necessary files
COPY corems/ /home/corems/corems
COPY examples/notebooks/*.ipynb examples/scripts/ /home/corems/examples/
COPY README.md disclaimer.txt requirements.txt setup.py SettingsCoreMS.json /home/corems/

# Install dependencies and clean up in single layer
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install pythonnet && \
    sed -i 's/psycopg2~/psycopg2-binary~/g' requirements.txt && \
    python3 -m pip install -U -r requirements.txt && \
    python3 -m pip install jupyter && \
    python3 setup.py install && \
    rm -rf /home/corems/corems /home/corems/setup.py

EXPOSE 8888

CMD jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
