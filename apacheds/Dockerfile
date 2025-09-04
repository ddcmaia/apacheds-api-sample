FROM --platform=linux/amd64 openjdk:11.0.16-jdk

# Based on https://registry.hub.docker.com/u/jjhughes57/apacheds-docker/

RUN apt-get update && apt-get install -y xinetd ldap-utils curl jq gettext-base

ADD https://dlcdn.apache.org//directory/apacheds/dist/2.0.0.AM27/apacheds-2.0.0.AM27-amd64.deb /tmp/installer.deb
RUN dpkg -i /tmp/installer.deb
RUN mkdir /templates && mkdir /ldifs

COPY files/health_check.sh /root/health_check.sh
COPY files/healthchk /etc/xinetd.d/healthchk
COPY ldifs/* /ldifs/

RUN echo 'healthchk      11001/tcp' >> /etc/services

EXPOSE 10389 10636 11001

COPY templates/* /templates/
COPY bin/* /usr/local/bin/
COPY lib/* /usr/local/lib/apacheds/
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
