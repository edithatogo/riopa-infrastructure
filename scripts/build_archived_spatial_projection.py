#!/usr/bin/env python3
"""Build the Stats NZ Meshblock projection from a pinned archive packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from riopa_provenance.archived_spatial import (
    ArchivedPacketDescriptor,
    build_archived_arcgis_projection,
    download_archived_packet,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("descriptor", type=Path)
    parser.add_argument("--packet-root", required=True, type=Path)
    parser.add_argument("--records-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--base-name", default="meshblocks-2026")
    args = parser.parse_args()

    descriptor = ArchivedPacketDescriptor.from_path(args.descriptor)
    if args.download:
        download_archived_packet(descriptor, args.packet_root)
    result = build_archived_arcgis_projection(
        descriptor,
        packet_root=args.packet_root,
        records_dir=args.records_dir,
        output_dir=args.output_dir,
        base_name=args.base_name,
    )
    print(
        json.dumps(
            {
                "feature_count": result.feature_count,
                "capture_record_count": result.capture_record_count,
                "projection_record": str(result.projection_record_path),
                "geoparquet": str(result.materialization.geoparquet_path),
                "duckdb": str(result.materialization.duckdb_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
