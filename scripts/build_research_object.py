#!/usr/bin/env python3
import sys

from riopa_provenance.cli import main

if __name__ == "__main__":
    main(["research-object", *sys.argv[1:]])
