# rdns
Quickly look up reverse DNS names.  One of them or lots of them.

Look them up by IPv4 address:
```sh
$ rdns 192.0.43.7
# 192.0.43.7
192.0.43.7	icann.org.
```
Look them up by IPv6 address:
```sh
$ rdns 2001:500:88:200::8
# 2001:500:88:200::8
2001:500:88:200::8	iana.org.
```
Look up ranges of them:
```sh
$ rdns 192.0.43.7/29
# 192.0.43.7/29
192.0.43.0	# error: lookup 192.0.43.0: nodename nor servname provided, or not known
192.0.43.1	43-1.any.icann.org.
192.0.43.2	43-2.any.icann.org.
192.0.43.3	43-3.any.icann.org.
192.0.43.4	43-4.any.icann.org.
192.0.43.5	43-5.any.icann.org.
192.0.43.6	43-6.any.icann.org.
192.0.43.7	icann.org.
```
Look them up by forward name:
```sh
$ rdns arin.net
# arin.net
2001:500:4:c000::43	www.arin.net.
2001:500:4:c000::44	www.arin.net.
199.43.0.43	www.arin.net.
199.43.0.44	www.arin.net.
```
Look them up by all of the above at once:
```sh
$ rdns 192.0.43.7 2001:500:88:200::8 192.0.43.7/29 arin.net
# 192.0.43.7
192.0.43.7	icann.org.
# 2001:500:88:200::8
2001:500:88:200::8	iana.org.
# 192.0.43.7/29
192.0.43.0	# error: lookup 192.0.43.0: nodename nor servname provided, or not known
192.0.43.1	43-1.any.icann.org.
192.0.43.2	43-2.any.icann.org.
192.0.43.3	43-3.any.icann.org.
192.0.43.4	43-4.any.icann.org.
192.0.43.5	43-5.any.icann.org.
192.0.43.6	43-6.any.icann.org.
192.0.43.7	icann.org.
# arin.net
2001:500:4:c000::43	www.arin.net.
2001:500:4:c000::44	www.arin.net.
199.43.0.43	www.arin.net.
199.43.0.44	www.arin.net.
```
Errors go to stderr so they're easy to filter out if you're scanning a sparse net and don't care about failures:
```sh
$ rdns 4.2.2.0/27 2>/dev/null
# 4.2.2.0/27
4.2.2.1	a.resolvers.level3.net.
4.2.2.2	b.resolvers.level3.net.
4.2.2.3	c.resolvers.level3.net.
4.2.2.4	d.resolvers.level3.net.
4.2.2.5	e.resolvers.level3.net.
4.2.2.6	f.resolvers.level3.net.
4.2.2.12	test-record.level3.net.
```

## Installation
```sh
$ go install github.com/kevinwallace/rdns
```

Happy resolving.
