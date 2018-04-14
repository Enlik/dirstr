#!/bin/bash

: ${script:?}
: ${test_dir:?}

"$script" \
	--spec-file "$test_dir/paths" \
	--root-dir root_dir/ \
	--class a
