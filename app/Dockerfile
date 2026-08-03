FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        unzip \
        openssh-client \
    && curl -fsSLo /tmp/terraform.zip \
        https://releases.hashicorp.com/terraform/1.13.0/terraform_1.13.0_linux_amd64.zip \
    && unzip /tmp/terraform.zip -d /usr/local/bin \
    && rm /tmp/terraform.zip \
    && rm -rf /var/lib/apt/lists/*

COPY . /workspace

RUN terraform -chdir=/workspace/terraform-end-user init -backend=false

RUN pip install --no-cache-dir -r /workspace/app/requirements.txt

RUN ansible-galaxy collection install ibm.ibm_zos_core

WORKDIR /workspace/app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]