FROM registry.access.redhat.com/ubi8/ubi-minimal
LABEL maintainer "Red Hat OpenShift Dedicated SRE Team"

RUN mkdir /app
WORKDIR /app

COPY . ./

#RUN ["chmod", "+x", "./hack/generate_template.py"]
RUN microdnf install -y python3 python3-pip
# RUN pip3 freeze > requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install jq

RUN microdnf install procps-ng
RUN microdnf install perl
RUN curl -Lo /bin/ocm https://github.com/openshift-online/ocm-cli/releases/download/v0.1.30/ocm-linux-amd64
RUN chmod +x /bin/ocm
RUN curl -Lo /bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64
RUN chmod +x /bin/jq


ENTRYPOINT [ "/app/startup.sh" ]