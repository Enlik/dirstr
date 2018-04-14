#!/bin/bash

dir=$(dirname "$0") || exit 1
tmpdir=$(mktemp -d --tmpdir="$dir") || exit 1
echo "tmpdir: $tmpdir"


if [[ $# = 0 ]]; then
	test_dirs=( "$dir"/* )
else
	test_dirs=()
	for tmp; do
		test_dirs+=( "$dir/$tmp" )
	done
	unset tmp
fi


exec_test() {
	local ret

	local script=$(readlink -f "$dir/../dirstr.py") || exit 1
	local abs_test_dir=$(readlink -f "$test_dir") || exit 1
	local abs_test_tmpdir=$(readlink -f "$test_tmpdir") || exit 1


	(
		# Provide stable location for root_dir so tests can use this
		# (static) value (see outside-root-updir test).
		cd "$test_tmpdir" \
			&& \
			script="$script" \
			test_dir="$abs_test_dir" \
			"$abs_test_dir/run.sh" 2> >(tee "$abs_test_tmpdir/stderr")
	)
	ret=$?

	if [[ -e $test_dir/expected ]]; then
		[[ $ret = 0 ]] || return $ret
		diff -qr "$test_tmpdir/root_dir" "$test_dir/expected" || return $?
	else
		if [[ $ret = 0 ]]; then
			echo "expected failure but exited with success"
			return 1
		fi
	fi

	if [[ -e $test_dir/stderr ]]; then
		diff -u "$test_dir/stderr" "$test_tmpdir/stderr" || return $?
	fi
}

n_failed=0

for test_dir in "${test_dirs[@]}"; do
	[[ -e $test_dir/run.sh ]] || continue

	test_name=${test_dir##*/}

	echo "** $0: preparing and running $test_name **"

	test_tmpdir=$tmpdir/$test_name
	mkdir "$test_tmpdir" || exit 1
	cp -a "$test_dir/root_dir" "$test_tmpdir/" || exit 1

	exec_test
	ret=$?

	if [[ $ret = 0 ]]; then
		echo "PASS: $test_name"
	else
		echo "FAIL: $test_name (ret=$ret)"
		(( n_failed++ ))
	fi
done

echo
if [[ $n_failed = 0 ]]; then
	rm -rf -- "$tmpdir"
	echo "**** all tests passed ****"
	status=0
else
	[[ $n_failed = 1 ]] && s= || s=S
	echo "**** $n_failed TEST$s FAILED ****"
	status=1
fi
exit "$status"
