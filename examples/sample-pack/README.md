# Sample Knowledge Pack: Web API Security

A minimal working example of an ANDON Knowledge Pack.

## Purpose

This sample pack demonstrates the Knowledge Pack structure with:

- Domain keyword definitions for web API security topics
- Failure classification rules for common API errors (401, 403, CORS, rate limiting)
- Skill recommendations mapped to failure domains

## Usage

Copy this directory as a starting point for your own pack:

```bash
cp -r examples/sample-pack packs/my-pack
```

Then customize `knowledge-pack.yaml` and add your own skills under `skills/`.

See [CONTRIBUTING-PACKS.md](../../CONTRIBUTING-PACKS.md) for the full specification.

## License

Apache License 2.0. See [LICENSE](./LICENSE).
