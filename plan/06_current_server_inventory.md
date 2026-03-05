# 6) Current Server Inventory (for project handover)

Collected on: 2026-03-05

## Host and OS
- OS: Ubuntu 24.04.3 LTS (Noble)
- Kernel: `6.8.0-100-generic`
- Virtualization: KVM
- Hostname: `ubuntu`

## Hardware / capacity
- CPU: 2 vCPU (`AMD EPYC-Milan Processor` virtualized)
- RAM: 1.8 GiB total
  - used at snapshot: 1.6 GiB
  - swap: 11 GiB (3.4 GiB used)
- Root disk: 77 GiB total
  - used at snapshot: 60 GiB (79%)
  - available: 17 GiB

Important capacity note:
- Memory is tight for running API + workers + web + DB on one host.
- Disk headroom is moderate but should be monitored closely.

## Network and interfaces
- Public IPv4: `217.154.251.5/32` on `ens6`
- Public IPv6 present on `ens6`
- VPN interfaces: `tun0`, `wg0`
- Docker bridge networks present (`docker0`, custom bridges)

## Open/listening services (relevant)
Publicly listening:
- `80/tcp` -> Nginx
- `443/tcp` -> Nginx
- `2405/tcp` -> SSH
- `1194/udp` -> OpenVPN
- `51820/udp` -> WireGuard

Loopback-only internal DB/cache:
- `127.0.0.1:5432` -> PostgreSQL
- `127.0.0.1:3306` -> MariaDB
- `127.0.0.1:6379` -> Redis
- several local node/gunicorn ports in use by existing apps

## Firewall and security baseline
- UFW status: inactive
- Fail2ban installed and running
- SSH is active on non-standard port 2405

## Installed toolchain and software likely useful
Core tools:
- `git 2.43.0`
- `curl 8.5.0`
- `jq 1.7`
- `gcc/g++ 13.3.0`
- `cmake 3.28.3`

Runtime/tooling:
- `python 3.12.3`, `pip 24.0`
- `node v20.20.0`, `npm 10.8.2`, `yarn 1.22.22`
- `openjdk 21.0.10`, `javac 21.0.10`
- `docker 28.2.2`

Web/data stack:
- `nginx 1.24.0`
- `postgresql client 15.15` (service running)
- `mariadb 10.11.14` (service running)
- `redis 7.0.15` (service running)
- `certbot 2.9.0`

## Running systemd services (project-relevant subset)
- `nginx.service`
- `postgresql@15-main.service`
- `mariadb.service`
- `redis-server.service`
- `docker.service`, `containerd.service`
- `fail2ban.service`
- existing custom app service: `musicstats-api.service`

## What someone without access needs to replicate
1. VPS profile recommendation
- Minimum for GT stack: 4 vCPU, 8 GB RAM, 120+ GB SSD
- Preferred for launch: 8 vCPU, 16 GB RAM, managed backups

2. Base software install
- Ubuntu 24.04 LTS
- Python 3.12, FastAPI stack, Gunicorn/Uvicorn
- PostgreSQL 15+
- Redis 7+
- Nginx + Certbot
- systemd service files for API, workers, sim, bots

3. DNS and domain setup
- `A` and `AAAA` records for `gt.nikolai-linschmann.de`
- TLS via certbot and Nginx server block

4. Security and ops baseline
- Enable firewall (UFW/nftables)
- lock DB/cache to localhost/private network
- configure backups for PostgreSQL (daily + WAL)
- logs and alerts for API errors, queue lag, tick failures

5. Deployment model
- systemd units:
  - `gt-api.service`
  - `gt-worker.service`
  - `gt-sim.service`
  - `gt-bot.service`
  - `gt-rt.service`

## Risks on current host if used as-is
- RAM pressure already high; OOM risk during peak simulation cycles.
- Root disk at 79%; log growth + DB growth can become critical.
- UFW inactive; network hardening should be done before production go-live.
