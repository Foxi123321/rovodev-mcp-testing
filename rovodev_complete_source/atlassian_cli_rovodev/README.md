# RovoDev CLI

This repository contains source code for the RovoDev CLI app.

## Documentation

- Experience ID (xid): The CLI supports an `--xid` flag to tag requests and analytics. Defaults to `rovodev-cli`. `--application-id` is deprecated and treated as an alias.


- **[Serve Mode Documentation](docs/serve/README.md)** - Comprehensive guide for running RovoDev CLI in server mode with REST API and SSE streaming

## Development

```bash
uv sync
uv run rovodev --help
```
