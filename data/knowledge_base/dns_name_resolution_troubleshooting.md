# DNS Name Resolution Troubleshooting

## Symptoms
- Hostname or website cannot be found.
- Server works by IP address but not by hostname.
- Only some users or locations are affected.
- Recently changed DNS record does not appear to have taken effect.

## Possible causes
- Incorrect DNS server configured on the client.
- Missing, incorrect, or stale DNS record.
- Stale local DNS cache.
- DNS server unavailable or unreachable.
- VPN provides incorrect DNS settings.
- DNS zone replication or record propagation is incomplete.
- Typographical error or incorrect DNS suffix.

## Information to collect
Exact hostname/FQDN, user/device/location, network or VPN status, whether access by IP works, start time, and recent DNS changes.

## Troubleshooting
1. Verify hostname spelling and expected DNS suffix.
2. Run `ipconfig /all` and inspect DNS server addresses and suffixes.
3. Run `nslookup <hostname>` to query the configured resolver.
4. If authorized, compare with `nslookup <hostname> <dns-server-address>` using the organization's designated resolver.
5. If the local cache is suspected, run `ipconfig /flushdns`, then repeat the lookup.
6. Ask DNS administration to verify record name, type (A, AAAA, CNAME), target, TTL, zone, and replication.
7. Check VPN/network routing if the client cannot reach its DNS server.

## Useful commands
- `ipconfig /all` — show interface and DNS configuration.
- `ipconfig /flushdns` — clear local DNS cache.
- `nslookup <hostname>` — query DNS.
- `nslookup <hostname> <dns-server-address>` — query a specific resolver.
- `ping <hostname>` — may test resolution/reachability, but ICMP can be blocked.

A failed ping alone does not prove DNS is broken. Do not use public resolvers for internal names unless approved.

## Resolution examples
- Clearing a stale client cache restored the current lookup.
- DNS administrator corrected an incorrect record.
- VPN profile was corrected to provide the approved internal DNS resolver.
- DNS team restored an unavailable DNS service.

These examples are illustrative. Escalate record/zone issues to DNS administration and resolver reachability/routing issues to network support.

## Metadata
Category: Network | Subcategory: DNS / Name Resolution
Keywords: DNS, hostname, nslookup, resolver, cache, name resolution
