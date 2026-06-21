#!/usr/bin/env python3
"""
subnet_calc.py

A small VLSM (Variable Length Subnet Masking) calculator.

Wrote this after one too many late nights doing VLSM by hand
during a network redesign project. Figured I'd clean it up and
share it in case it's useful to anyone else.

Usage:
    python3 subnet_calc.py 192.168.1.0/24
    python3 subnet_calc.py 10.0.0.0/16 --hosts 500 200 50 20

-- ML
"""

import argparse
import ipaddress
import sys


def smallest_prefix_for_hosts(host_count: int) -> int:
    """Return the smallest /prefix that can accommodate host_count usable hosts."""
    needed = host_count + 2  # network + broadcast
    for prefix in range(32, 0, -1):
        if (2 ** (32 - prefix)) >= needed:
            return prefix
    raise ValueError("Host count too large for IPv4")


def vlsm(base_network: str, host_requirements: list[int]):
    """
    Allocate subnets of a base network using VLSM, largest requirement first.
    Returns a list of (requirement, allocated_network) tuples.
    """
    network = ipaddress.ip_network(base_network, strict=False)
    # Sort largest first -- this is the classic VLSM allocation strategy,
    # since allocating big blocks first avoids fragmentation.
    sorted_reqs = sorted(enumerate(host_requirements), key=lambda x: -x[1])

    allocations = [None] * len(host_requirements)
    cursor = int(network.network_address)
    network_end = int(network.broadcast_address)

    for original_index, hosts in sorted_reqs:
        prefix = smallest_prefix_for_hosts(hosts)
        block_size = 2 ** (32 - prefix)

        # Align cursor to the block boundary
        if cursor % block_size != 0:
            cursor += block_size - (cursor % block_size)

        if cursor + block_size - 1 > network_end:
            raise ValueError(
                f"Not enough address space remaining for a /{prefix} "
                f"block to satisfy {hosts} hosts"
            )

        subnet = ipaddress.ip_network(
            (ipaddress.IPv4Address(cursor), prefix), strict=False
        )
        allocations[original_index] = (hosts, subnet)
        cursor += block_size

    return allocations


def print_allocations(base_network: str, allocations):
    print(f"\nVLSM allocation for {base_network}\n")
    header = f"{'Hosts needed':<14}{'Subnet':<20}{'Usable range':<33}{'Broadcast':<16}"
    print(header)
    print("-" * len(header))
    for hosts, subnet in allocations:
        hosts_list = list(subnet.hosts())
        if hosts_list:
            usable = f"{hosts_list[0]} - {hosts_list[-1]}"
        else:
            usable = "n/a"
        print(f"{hosts:<14}{str(subnet):<20}{usable:<33}{str(subnet.broadcast_address):<16}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Quick VLSM subnet calculator."
    )
    parser.add_argument(
        "network",
        help="Base network in CIDR notation, e.g. 192.168.1.0/24"
    )
    parser.add_argument(
        "--hosts",
        nargs="+",
        type=int,
        default=None,
        help="List of host counts to allocate subnets for, e.g. --hosts 100 50 20 10. "
             "If omitted, just prints the basic info for the base network."
    )
    args = parser.parse_args()

    try:
        network = ipaddress.ip_network(args.network, strict=False)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not args.hosts:
        print(f"\nNetwork:        {network}")
        print(f"Netmask:        {network.netmask}")
        print(f"Network addr:   {network.network_address}")
        print(f"Broadcast addr: {network.broadcast_address}")
        print(f"Usable hosts:   {network.num_addresses - 2}")
        print("\nTip: pass --hosts to compute a VLSM allocation, e.g.")
        print(f"     python3 subnet_calc.py {args.network} --hosts 100 50 20\n")
        return

    try:
        allocations = vlsm(str(network), args.hosts)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print_allocations(str(network), allocations)


if __name__ == "__main__":
    main()
