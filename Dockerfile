FROM python:3.5
ADD dist/test*.whl .
ADD requirements.txt .
RUN pip install -r requirements.txt
RUN pip install test*.whl 
RUN pip install uwsgi

# install Consul CLI tool
RUN apt-get update && apt-get install -y jq unzip
RUN wget https://releases.hashicorp.com/consul/0.7.1/consul_0.7.1_linux_amd64.zip
RUN unzip consul_0.7.1_linux_amd64.zip -d /usr/local/bin/
RUN wget https://releases.hashicorp.com/vault/0.6.4/vault_0.6.4_linux_amd64.zip && \
    unzip vault_0.6.4_linux_amd64 && \
    mv vault /usr/local/bin
ADD scripts/env-init.sh .
ADD scripts/startup.sh .
CMD ["./startup.sh"]  