# VPN Connection Troubleshooting

## Symptoms
- VPN client cannot connect, authentication fails, or connection drops.
- VPN connects but internal applications or servers are unreachable.
- Client reports a certificate, gateway, or network error.

## Possible causes
- Expired, missing, or untrusted device/gateway certificate.
- Incorrect or expired credentials, locked account, or MFA failure.
- Internet, firewall, proxy, or router prevents access to the VPN gateway.
- Incorrect VPN profile, gateway address, protocol, or outdated client.
- Missing access-group membership or access-policy restriction.
- VPN gateway outage.

## Information to collect
User and device identifiers, start time, VPN client/version, exact error, network type, whether others are affected, and recent password/device changes. Never ask for passwords, MFA codes, or private keys.

## Troubleshooting
1. Confirm internet access without VPN.
2. Check the organization's service-status dashboard and whether multiple users are affected.
3. Verify the approved VPN gateway and profile.
4. Check account status, password expiry, and MFA using authorized identity tools.
5. For certificate errors, verify device time and certificate validity; follow the approved renewal process.
6. If connected but internal resources fail, check DNS and routing and involve network support.
7. Reinstall/reset the VPN client only through approved endpoint procedures.

## Useful Windows commands
- `ipconfig /all` — inspect network configuration.
- `nslookup <internal-hostname>` — check DNS resolution.
- `tracert <internal-hostname>` — inspect the route.
- `route print` — display local routes.
- `ipconfig /flushdns` — clear local DNS cache.

## Resolution examples
- Expired endpoint certificate renewed through approved certificate management.
- Identity team corrected MFA registration.
- Local internet connectivity restored.
- Network operations restored an unavailable VPN gateway.

These examples are illustrative. Escalate gateway, routing, or widespread issues to network/VPN support; account/MFA issues to identity support; and client/certificate issues to endpoint support.

## Metadata
Category: Network | Subcategory: VPN / Remote Access
Keywords: VPN, remote access, certificate, MFA, gateway, connection failure
