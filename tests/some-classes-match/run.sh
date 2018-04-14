#!/bin/bash

: ${script:?}
: ${test_dir:?}

"$script" \
	--spec-file "$test_dir/paths" \
	--root-dir root_dir \
	--class a

# a ./dir2/dir3/dir4/file4
# b ./dir2/dir3/dir4
# Note that dir3 is being taken due to file4.
