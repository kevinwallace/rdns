package main

import (
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
)

func main() {
	flag.Parse()
	for _, arg := range flag.Args() {
		if ipnets, err := resolveArg(arg); err != nil {
			fmt.Fprintf(os.Stderr, "# couldn't resolve %s: %s\n", arg, err)
		} else {
			fmt.Printf("# %s\n", arg)
			for _, ipnet := range ipnets {
				ip := ipnet.IP
				for ipnet.Contains(ip) {
					line := ip.String() + "\t"
					names, err := net.LookupAddr(ip.String())
					line += strings.Join(names, " ")
					if err != nil {
						line += fmt.Sprintf(" # %s", err)
					}
					fmt.Println(line)
					ip = next(ip)
				}
			}
		}
	}
}

// next returns the next IP address after ip, or nil if there is no such address.
func next(ip net.IP) net.IP {
	next := make(net.IP, len(ip))
	copy(next, ip)
	for i := len(next) - 1; i >= 0; i-- {
		next[i]++
		if next[i] != 0 {
			return next
		}
	}
	return nil
}

// resolveArg parses an argument of one of the following forms:
// * 1.2.3.4
// * 1.2.3.4/24
// * 2001::
// * 2001::/16
// * hostname.example.com
// If the given address is a hostname, it is resolved to all of its A and AAAA records.
// It returns the specified networks as a slice of net.IPNet.
func resolveArg(arg string) ([]net.IPNet, error) {
	parts := strings.SplitN(arg, "/", 2)
	ips, err := resolveHost(parts[0], len(parts) == 1)
	if err != nil {
		return nil, err
	}

	ipnets := make([]net.IPNet, len(ips))
	for i, ip := range ips {
		if len(parts) > 1 {
			if _, ipnet, err := net.ParseCIDR(ip.String() + "/" + parts[1]); err != nil {
				return nil, err
			} else {
				ipnets[i] = *ipnet
			}
		} else {
			ipnets[i].IP = ip
			ipnets[i].Mask = net.CIDRMask(len(ip)*8, len(ip)*8)
		}
	}
	return ipnets, nil
}

func resolveHost(host string, canLookup bool) ([]net.IP, error) {
	ip := parseIP(host)
	if ip != nil {
		return []net.IP{ip}, nil
	}
	if canLookup {
		return net.LookupIP(host)
	}
	return nil, fmt.Errorf("can't parse IP")
}

func parseIP(s string) net.IP {
	ip := net.ParseIP(s)
	// net.ParseIP provides no way to distinguish "::ffff:1.2.3.4" from "1.2.3.4";
	// this attempts to do so by assuming any IPv6 address contains a ':'.
	// I think this is an accurate heuristic, but I am not sure of it.
	if !strings.Contains(s, ":") {
		ip = ip.To4()
	}
	return ip
}
