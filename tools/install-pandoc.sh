#!/bin/sh
# Install a pinned pandoc release (Linux amd64) into ~/.local, no root needed.
# Used both locally and in CI so builds use the same version everywhere.
set -eu

VERSION=3.14
SHA256=c5f4720cdefb3f7bdc5d07202ef579feef0d1370773c873804dd8fdaa8c4f1b8

PREFIX="${PREFIX:-$HOME/.local}"
URL="https://github.com/jgm/pandoc/releases/download/$VERSION/pandoc-$VERSION-linux-amd64.tar.gz"

if [ "$("$PREFIX/bin/pandoc" --version 2>/dev/null | head -n1)" = "pandoc $VERSION" ]; then
    echo "pandoc $VERSION already installed in $PREFIX/bin"
    exit 0
fi

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

curl -fsSL "$URL" -o "$tmp/pandoc.tar.gz"
echo "$SHA256  $tmp/pandoc.tar.gz" | sha256sum -c -

# The tarball contains pandoc-$VERSION/bin/pandoc and pandoc-$VERSION/share/...
mkdir -p "$PREFIX"
tar -xzf "$tmp/pandoc.tar.gz" -C "$PREFIX" --strip-components=1
echo "Installed pandoc $VERSION to $PREFIX/bin"
