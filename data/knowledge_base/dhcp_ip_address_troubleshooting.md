# DHCP and IP Address Troubleshooting

## Symptoms
- Windows shows an address beginning with `169.254`.
- Device reports limited/no network connectivity.
- Device cannot reach its default gateway.
- Connectivity returns temporarily after reconnecting.
- Multiple devices in one VLAN or office area are affected.

## Possible causes
- DHCP server or DHCP relay unavailable.
- DHCP scope has no free addresses.
- VLAN, routing, or firewall prevents reaching DHCP.
- Incorrect DHCP scope options (subnet, gateway, DNS).
- Duplicate IP or incorrect static configuration.
- Cable, Wi-Fi, switch port, or access-point problem.
- Incorrect lease or reservation configuration.

## Information to collect
User/device, physical location, wired or wireless connection, network/VLAN/SSID, IP/subnet/gateway/DNS details, affected scope, and start time.

## Troubleshooting
1. Check cable connection or correct Wi-Fi association; compare nearby devices.
2. Run `ipconfig /all` and inspect IPv4 address, subnet, gateway, DHCP enabled status, DHCP server, and lease.
3. An address in `169.254.0.0/16` is APIPA and commonly means the client did not obtain an IPv4 DHCP lease; it does not identify the root cause by itself.
4. If permitted, run `ipconfig /release` followed by `ipconfig /renew`.
5. Compare the resulting configuration with a working device on the same network.
6. Ask network operations to check DHCP service, scope utilization, scope options, relay/IP helper, VLAN, reservations, and exclusions.
7. Do not assign an arbitrary static IP as a workaround.

## Useful commands
- `ipconfig /all` — display IP configuration.
- `ipconfig /release` — release current DHCP lease.
- `ipconfig /renew` — request a DHCP lease.
- `ipconfig /flushdns` — clear DNS cache; this does not renew a DHCP lease.
- `getmac /v` — display adapter MAC addresses; handle output according to policy.

## Resolution examples
- DHCP service reachability restored and device obtained a valid lease.
- Network team corrected scope exhaustion.
- Switch port was assigned to the correct VLAN.
- DHCP administrator corrected the default-gateway scope option.

These examples are illustrative. Escalate DHCP server, relay, VLAN, and scope issues to network operations; isolated adapter/OS issues to endpoint support.

## Metadata
Category: Network | Subcategory: DHCP / IP Addressing
Keywords: DHCP, APIPA, 169.254, IP address, lease, gateway, VLAN
