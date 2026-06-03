#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
VERSION="$(python3 -c "import pathlib,re; text=pathlib.Path('$ROOT_DIR/pyproject.toml').read_text(); print(re.search(r'^version = \"([^\"]+)\"', text, re.M).group(1))")"
PKG_NAME="local-whisper-dictation"
ARCH="${ARCH:-amd64}"
BUILD_ROOT="$ROOT_DIR/build/linux-deb"
PKG_ROOT="$BUILD_ROOT/${PKG_NAME}_${VERSION}_${ARCH}"
APP_DIR="$PKG_ROOT/opt/local-whisper-dictation"

rm -rf "$BUILD_ROOT"
mkdir -p "$APP_DIR" "$PKG_ROOT/DEBIAN" "$PKG_ROOT/usr/bin" "$PKG_ROOT/usr/share/applications"

cp -R "$ROOT_DIR/src" "$APP_DIR/src"
cp "$ROOT_DIR/pyproject.toml" "$APP_DIR/pyproject.toml"
cp "$ROOT_DIR/requirements.txt" "$APP_DIR/requirements.txt"
cp "$ROOT_DIR/app_launcher.py" "$APP_DIR/app_launcher.py"

if [ -d "$ROOT_DIR/dist/wheelhouse" ]; then
  cp -R "$ROOT_DIR/dist/wheelhouse" "$APP_DIR/wheelhouse"
fi

install -m 0755 "$ROOT_DIR/packaging/linux/local-dictation.sh" "$PKG_ROOT/usr/bin/local-dictation"
install -m 0644 "$ROOT_DIR/packaging/linux/local-whisper-dictation.desktop" "$PKG_ROOT/usr/share/applications/local-whisper-dictation.desktop"
install -m 0755 "$ROOT_DIR/packaging/linux/postinst.sh" "$PKG_ROOT/DEBIAN/postinst"
install -m 0755 "$ROOT_DIR/packaging/linux/postrm.sh" "$PKG_ROOT/DEBIAN/postrm"

cat > "$PKG_ROOT/DEBIAN/control" <<EOF
Package: $PKG_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Depends: python3, python3-venv, python3-pip, libportaudio2
Maintainer: Local Whisper Dictation
Description: Local faster-whisper tray dictation app.
 A local-first dictation app using PySide6, sounddevice, and faster-whisper.
EOF

dpkg-deb --build "$PKG_ROOT" "$ROOT_DIR/dist/${PKG_NAME}_${VERSION}_${ARCH}.deb"
echo "Built $ROOT_DIR/dist/${PKG_NAME}_${VERSION}_${ARCH}.deb"
