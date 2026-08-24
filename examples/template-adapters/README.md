# Synthetic template adapter examples

Status: `example` — these records demonstrate additive adapter boundaries
without contacting a source or writing a live payload.

The examples cover connector, archive, transformation and analytics roles.

```sh
uv run pytest tests/test_template_adapter_examples.py -q
```

The JSON fixture is a contract example, not a production adapter or a live
source claim. Credentials, network requests, national coverage and operational
use are intentionally absent.
