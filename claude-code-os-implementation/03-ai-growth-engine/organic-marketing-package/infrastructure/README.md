# Infrastructure

Scripts, configuration, and deployment resources for the Organic Marketing platform.

## Structure

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Setup, deployment, and maintenance scripts |
| `docker/` | Docker and container configuration |
| `config/` | Environment and service configuration templates |

## Scripts

Setup and operational scripts migrated from the package root and `scripts/` directory:

- `scripts/setup-all.sh` - Install dependencies for all packages
- `scripts/start-services.sh` - Start all services
- `scripts/test-all.sh` - Run tests across all packages
- `scripts/verify-*.sh` - Verification and validation scripts

## Previous Location

Migrated from `scripts/` and root-level `.sh` files in the package root.
