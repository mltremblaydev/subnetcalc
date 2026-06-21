# subnet-calc

A small Python tool for quick VLSM (Variable Length Subnet Masking) calculations.

Built this after one too many late nights doing VLSM by hand during a network
redesign project. Figured I'd clean it up a bit and share it.

## Usage

Basic network info:

```bash
python3 subnet_calc.py 192.168.1.0/24
```

VLSM allocation across multiple subnets, largest requirement first:

```bash
python3 subnet_calc.py 192.168.1.0/24 --hosts 100 50 20 10
```

Output:

```
VLSM allocation for 192.168.1.0/24

Hosts needed  Subnet              Usable range                     Broadcast
-----------------------------------------------------------------------------------
100           192.168.1.0/25      192.168.1.1 - 192.168.1.126      192.168.1.127
50            192.168.1.128/26    192.168.1.129 - 192.168.1.190    192.168.1.191
20            192.168.1.192/27    192.168.1.193 - 192.168.1.222    192.168.1.223
10            192.168.1.224/28    192.168.1.225 - 192.168.1.238    192.168.1.239
```

## Requirements

Python 3.9+ (uses the built-in `ipaddress` module, no external dependencies)

## Notes

This was a personal project I put together for work, sharing here in case
it's useful to anyone else doing network design. Pull requests welcome,
though fair warning I don't check this repo too often.

See also: the maintenance log attached to this account's recent activity,
and the change log doc in [Releases](../../releases) if you're looking for
the Server Room B documentation.

-- ML
