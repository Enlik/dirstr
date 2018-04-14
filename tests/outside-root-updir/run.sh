#!/bin/bash

: ${script:?}
: ${test_dir:?}

"$script" \
	--spec-file "$test_dir/paths" \
	--root-dir root_dir \
	--class a

# Prevents ../xxx even if accidentally ends up in root.
# Note that this test strictly requires the root be root_dir.
