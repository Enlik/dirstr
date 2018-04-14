#!/usr/bin/env python3

#   Copyright 2018 Sławomir Nizio
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import argparse
import errno
import os
import os.path
import sys
import stat


def parse_args():
    description = ("Make a directory content (by removing items) according to",
                   "a specification file.",
                   "Note that behaviour and file format can change in newer",
                   "versions.")
    parser = argparse.ArgumentParser(
        description=" ".join(description))
    parser.add_argument("--spec-file", type=str, required=True,
                        help="file that describes directory structure")
    parser.add_argument("--root-dir", type=str, required=True,
                        help="Root directory (paths in the file "
                        "are related to it)")
    parser.add_argument("--class", dest="class_", metavar="CLASS",
                        type=str, required=True,
                        help="Items selection from the specification file")
    parser.add_argument("--ignore-missing-from-class",
                        dest="ign_missing_class",
                        metavar="CLASS", action='append',
                        type=str, default=[],
                        help="Makes missing files from this class nonfatal")
    args = parser.parse_args()
    return args


def main(src_file, root_dir, class_to_use, ign_missing_class):
    with open(src_file) as f:
        spec = f.read()

    spec_lines = spec.splitlines()

    only_in_fs, only_in_spec = compare_dir_with_spec(root_dir, spec_lines)

    def check_handle_message(print_fmt, var, msg_func):
        disp_limit = 10
        if var:
            msg = [print_fmt.format(len(var), disp_limit)] + var[:disp_limit]
            msg_func(msg)

    check_handle_message(
        "additional {} item(s) not present in spec (showing up to {}):",
        sorted(only_in_fs), fatal_error)

    missing, to_stay, to_remove = walk_spec_lines(
        root_dir, spec_lines, class_to_use, ign_missing_class, only_in_spec)

    to_remove = filter_removal_list(to_stay, to_remove)

    missing_ignored = [x[1] for x in missing if x[0]]
    missing_not_ignored = [x[1] for x in missing if not x[0]]

    check_handle_message("(ignored) already missing: {} (showing up to {}):",
                         missing_ignored, print_warning)
    check_handle_message("already missing: {} (showing up to {}):",
                         missing_not_ignored, fatal_error)

    print("to remove:", len(to_remove))

    do_removal(root_dir, to_remove)


def compare_dir_with_spec(root_dir, spec_lines):
    def onerror(exc):
        raise exc

    lines = [parse_spec_line(x)[1] for x in spec_lines]
    lines_normalized = {os.path.normpath(x): x for x in lines}

    fs_items = set()

    # In case the first argument of os.path.join has a slash at the end, new
    # one is not added. Handle it, so the path calculation is correct.
    root_dir_sanitized = root_dir.rstrip(os.path.sep)

    def cut_root_dir(path):
        return path[len(root_dir_sanitized)+1:]

    for root, dirs, files in os.walk(root_dir_sanitized, onerror=onerror):
        for f in files:
            path = os.path.join(root, f)
            fs_items.add(cut_root_dir(path))

        for d in dirs:
            # Unfortunately, symlinks to directories go to this list even with
            # followlinks=False (default).
            path = os.path.join(root, d)
            if os.path.islink(path):
                fs_items.add(cut_root_dir(path))

        directory = cut_root_dir(root)
        if not directory:
            directory = "."
        fs_items.add(directory)

    only_in_fs = fs_items - lines_normalized.keys()
    only_in_spec = set([lines_normalized[x]
                        for x in lines_normalized.keys()-fs_items])

    return only_in_fs, only_in_spec


def print_warning(msg):
    if not isinstance(msg, str):
        msg = "\n".join(msg)
    print(msg, file=sys.stderr)


def fatal_error(msg, summary=True, exit_st=1):
    print_warning(msg)
    if summary:
        print_warning("aborting")
    exit(exit_st)


def walk_spec_lines(root_dir, spec_lines,
                    class_to_use, ign_missing_class, items_only_in_spec):
    missing = []
    to_stay = set()
    to_remove = []

    for line in spec_lines:
        class_, path = parse_spec_line(line)

        abort_if_outside_root(root_dir, path)

        if path in items_only_in_spec:
            missing += [(class_ in ign_missing_class, path)]
            continue

        if class_ == class_to_use:
            path_items = path.split(os.path.sep)
            for i in range(1, len(path_items)+1):
                to_stay.add(os.path.join(*path_items[:i]))
        else:
            to_remove += [path]

    return missing, to_stay, to_remove


def parse_spec_line(line):
    return line.split(" ", 1)


def abort_if_outside_root(root_dir, path):
    def path_at_updir(path):
        return os.path.normpath(path).startswith("../")

    def path_outside_root(root_dir, path):
        dest_path = os.path.join(root_dir, path)

        common_with_root_dir = os.path.commonpath(
            list(map(os.path.normpath, [root_dir, dest_path])))

        path_ok = (common_with_root_dir and
                   os.path.samefile(root_dir, common_with_root_dir))

        return not path_ok

    if path_at_updir(path) or path_outside_root(root_dir, path):
        fatal_error("Path outside root: '{}'".format(path),
                    exit_st=2)


def filter_removal_list(to_stay, to_remove):
    return [x for x in to_remove if x not in to_stay]


def do_removal(root_dir, to_remove):
    for path in to_remove:
        dest_path = os.path.join(root_dir, path)

        # Guard against attempt to remove "<root>/." which yields e.g.:
        # OSError: [Errno 22] Invalid argument: 'root_dir/.'
        # additionally, it's not necessary to try to remove it anyway.
        if os.path.samefile(root_dir, dest_path):
            continue

        try:
            os.rmdir(dest_path)
        except NotADirectoryError:
            os.remove(dest_path)


if __name__ == "__main__":
    args = parse_args()
    main(args.spec_file, args.root_dir, args.class_, args.ign_missing_class)
