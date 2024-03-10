FROM  python:rc-alpine3.10

COPY ./ /app

WORKDIR /app

RUN pip3 install jsonschema requests

ENV QBIT_URL="http://127.0.0.1:8080/api/v2/" \
    QBIT_USERNAME="" \
    QBIT_PASSWORD="" \
    VERBOSITY=0

VOLUME "/config"

CMD ["/usr/local/bin/python3","qbit_ratio_manager.py", \
    "--config_folder", "/config", \
    "--url", "$QBIT_URL", \
    "--username", "$QBIT_USERNAME", \
    "--password", "$QBIT_PASSWORD", \
    "--verbose"]
