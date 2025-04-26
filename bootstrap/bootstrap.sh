exec /app/bootstrap.sh \
  --user-configs-dir /bootstrap/user-configs \
  --group-configs-dir /bootstrap/group-configs \
  --admin-username "$LLDAP_LDAP_USER_DN" \
  --admin-password "$LLDAP_LDAP_USER_PASS"