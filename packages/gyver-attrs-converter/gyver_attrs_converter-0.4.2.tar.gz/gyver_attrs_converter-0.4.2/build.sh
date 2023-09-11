#!/bin/sh

versions=("3.9" "3.10" "3.11")
compat=("musllinux_1_1" "manylinux_2_17" "manylinux_2_28" "manylinux_2_34")
target="x86_64-unknown-linux-gnu"

for version in $versions; do
    for build in $compat; do
        maturin build \
            --release \
            --target "$target" \
            --interpreter $(which "python${version}") \
            --compatibility "$build" \
            --zig
    done
done

# for version in "3.9" "3.10" "3.11"; do
#     maturin build --release --target --zig --interpreter $(which "python${version}")
# done
