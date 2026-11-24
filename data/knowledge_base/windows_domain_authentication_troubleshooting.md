# Windows Domain Authentication Troubleshooting

## Symptoms
- User cannot sign in to a domain-joined Windows computer.
- Account is reported locked, disabled, or password-invalid.
- User signs in locally but cannot access domain resources.
- Remote sign-in fails while office sign-in works.
- Applications repeatedly prompt for domain credentials.

## Possible causes
- Incorrect password or keyboard layout.
- Expired password, locked, or disabled account.
- Device cannot contact a domain controller.
- DNS cannot locate domain services.
- Device time differs significantly from domain time.
- Broken computer-account trust relationship.
- User lacks permission to a resource.
- Recent account/group/policy changes have not taken effect.

## Information to collect
User ID (never password), device name/asset ID, exact error and timestamp, LAN/Wi-Fi/VPN status, whether others are affected, recent password/device changes, and whether the problem affects sign-in or one resource.

Never request passwords, MFA/recovery codes, or authentication tokens. Avoid repeated password guesses that may trigger lockout.

## Troubleshooting
1. Use authorized identity tools to check account existence, enabled/locked state, and password expiry.
2. Confirm corporate network or approved VPN connectivity.
3. Check DNS configuration with `ipconfig /all`.
4. Check domain-name resolution with `nslookup <domain-name>`.
5. If authorized, run `nltest /dsgetdc:<domain-name>` to request domain-controller discovery.
6. Compare device date, time, and time zone with the approved time source. Kerberos can fail when clocks differ beyond the environment's permitted tolerance.
7. For trust-relationship errors, record the message and escalate to endpoint/directory services. Do not unjoin/rejoin a production device without authorization and a recovery plan.
8. If sign-in succeeds but one resource is denied, ask the resource owner/identity team to verify permissions and group membership.

## Useful commands
- `whoami` — display current signed-in identity.
- `whoami /groups` — display groups in the current logon token.
- `ipconfig /all` — inspect network and DNS configuration.
- `nltest /dsgetdc:<domain-name>` — locate a domain controller.
- `w32tm /query /status` — inspect Windows Time status.

Use commands only within your authorization. Review output for sensitive account and infrastructure details.

## Resolution examples
- Identity support unlocked an account through the approved process.
- User completed the approved password-change flow.
- Network support corrected internal DNS so the device could locate a domain controller.
- Endpoint support restored managed time synchronization.
- Resource owner approved access and identity team updated group membership.

These examples are illustrative. Escalate account/MFA issues to identity support, domain-controller/DNS/replication issues to directory services, and device trust issues to endpoint support.

## Metadata
Category: Identity and Access | Subcategory: Windows Domain Authentication
Keywords: Active Directory, domain, authentication, account lockout, Kerberos, domain controller
