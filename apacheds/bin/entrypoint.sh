#!/bin/bash
# Main entrypoint for ApacheDS container.
# It configures optional features and handles replication before starting in the foreground.
set -e

source /usr/local/lib/apacheds/replication.sh

start_services() {
  /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default start
  /etc/init.d/xinetd start
  sleep 10
}

configure_admin_password() {
  if [ -n "${ADMIN_PASSWORD}" ]; then
    envsubst < "/templates/admin_password.ldif" > "/tmp/admin_password.ldif"
    ldapmodify -c -a -f /tmp/admin_password.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w secret
  else
    ADMIN_PASSWORD='secret'
  fi
}

enable_optional_features() {
  if [ -n "${NIS_ENABLED}" ]; then
    ldapmodify -c -a -f /ldifs/enable_nis.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
  fi

  if [ -n "${ACCESS_CONTROL_ENABLED}" ]; then
    ldapmodify -c -a -f /ldifs/access.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
    /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default stop
    /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default start
    sleep 10
  fi
}

configure_domain() {
  if [ -n "${DOMAIN_NAME}" ] && [ -n "${DOMAIN_SUFFIX}" ]; then
    envsubst < "/templates/partition.ldif" > "/tmp/partition.ldif"
    ldapmodify -c -a -f /tmp/partition.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
    ldapdelete "ads-partitionId=example,ou=partitions,ads-directoryServiceId=default,ou=config" -r -p 10389 -h localhost -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
    ldapdelete "dc=example,dc=com" -p 10389 -h localhost -D "uid=admin,ou=system" -r -w "${ADMIN_PASSWORD}"
    /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default stop
    /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default start
    sleep 10
    envsubst < "/templates/top_domain.ldif" > "/tmp/top_domain.ldif"
    ldapmodify -c -a -f /tmp/top_domain.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
  else
    DOMAIN_NAME="example"
    DOMAIN_SUFFIX="com"
  fi

  if [ -n "${ACCESS_CONTROL_ENABLED}" ]; then
    envsubst < "/templates/access_config.ldif" > "/tmp/access_config.ldif"
    ldapmodify -c -a -f /tmp/access_config.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
  fi
}

load_ldifs() {
  ldapmodify -c -a -f /ldifs/group-owner-schema.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
  ldapmodify -c -a -f /ldifs/seed.ldif -h localhost -p 10389 -D "uid=admin,ou=system" -w "${ADMIN_PASSWORD}"
}

start_replication() {
  enable_replication
  setup_replication
  nohup replica-check.sh &> /tmp/replica_check.log &
}

start_foreground() {
  /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default stop
  /etc/init.d/apacheds-2.0.0.AM28-SNAPSHOT-default console
}

main() {
  start_services
  configure_admin_password
  enable_optional_features
  configure_domain
  load_ldifs
  start_replication
  start_foreground
}

main "$@"
