#!/usr/bin/env sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
VERSION="$(python3 -c "import pathlib,re; text=pathlib.Path('$ROOT_DIR/pyproject.toml').read_text(); print(re.search(r'^version = \"([^\"]+)\"', text, re.M).group(1))")"
PKG_NAME="local-whisper-dictation"
RELEASE="${RELEASE:-1}"
RPM_ROOT="$ROOT_DIR/build/rpm"
STAGE="$RPM_ROOT/stage"
ARCHIVE="$RPM_ROOT/SOURCES/${PKG_NAME}-${VERSION}.tar.gz"

rm -rf "$RPM_ROOT"
mkdir -p "$RPM_ROOT/BUILD" "$RPM_ROOT/RPMS" "$RPM_ROOT/SOURCES" "$RPM_ROOT/SPECS" "$RPM_ROOT/SRPMS" "$STAGE/${PKG_NAME}-${VERSION}"

cp -R "$ROOT_DIR/src" "$STAGE/${PKG_NAME}-${VERSION}/src"
cp "$ROOT_DIR/pyproject.toml" "$STAGE/${PKG_NAME}-${VERSION}/pyproject.toml"
cp "$ROOT_DIR/requirements.txt" "$STAGE/${PKG_NAME}-${VERSION}/requirements.txt"
cp "$ROOT_DIR/app_launcher.py" "$STAGE/${PKG_NAME}-${VERSION}/app_launcher.py"
mkdir -p "$STAGE/${PKG_NAME}-${VERSION}/packaging/linux"
cp "$ROOT_DIR/packaging/linux/local-dictation.sh" "$STAGE/${PKG_NAME}-${VERSION}/packaging/linux/local-dictation.sh"
cp "$ROOT_DIR/packaging/linux/local-whisper-dictation.desktop" "$STAGE/${PKG_NAME}-${VERSION}/packaging/linux/local-whisper-dictation.desktop"
cp "$ROOT_DIR/packaging/linux/postinst.sh" "$STAGE/${PKG_NAME}-${VERSION}/packaging/linux/postinst.sh"
cp "$ROOT_DIR/packaging/linux/postrm.sh" "$STAGE/${PKG_NAME}-${VERSION}/packaging/linux/postrm.sh"
if [ -d "$ROOT_DIR/dist/wheelhouse" ]; then
  cp -R "$ROOT_DIR/dist/wheelhouse" "$STAGE/${PKG_NAME}-${VERSION}/wheelhouse"
fi

(cd "$STAGE" && tar -czf "$ARCHIVE" "${PKG_NAME}-${VERSION}")

cat > "$RPM_ROOT/SPECS/${PKG_NAME}.spec" <<EOF
Name:           $PKG_NAME
Version:        $VERSION
Release:        $RELEASE%{?dist}
Summary:        Local faster-whisper tray dictation app
License:        Private
BuildArch:      noarch
Requires:       python3
Requires:       python3-pip
Requires:       portaudio

%description
Local-first dictation app using PySide6, sounddevice, and faster-whisper.

%prep
%setup -q

%install
mkdir -p %{buildroot}/opt/local-whisper-dictation
cp -R src pyproject.toml requirements.txt app_launcher.py packaging %{buildroot}/opt/local-whisper-dictation/
if [ -d wheelhouse ]; then cp -R wheelhouse %{buildroot}/opt/local-whisper-dictation/; fi
mkdir -p %{buildroot}/usr/bin
install -m 0755 packaging/linux/local-dictation.sh %{buildroot}/usr/bin/local-dictation
mkdir -p %{buildroot}/usr/share/applications
install -m 0644 packaging/linux/local-whisper-dictation.desktop %{buildroot}/usr/share/applications/local-whisper-dictation.desktop

%post
/bin/sh /opt/local-whisper-dictation/packaging/linux/postinst.sh

%postun
if [ "\$1" = "0" ]; then
  rm -rf /opt/local-whisper-dictation/.venv
fi

%files
/opt/local-whisper-dictation
/usr/bin/local-dictation
/usr/share/applications/local-whisper-dictation.desktop
EOF

rpmbuild --define "_topdir $RPM_ROOT" -ba "$RPM_ROOT/SPECS/${PKG_NAME}.spec"
mkdir -p "$ROOT_DIR/dist"
find "$RPM_ROOT/RPMS" -name "*.rpm" -exec cp {} "$ROOT_DIR/dist/" \;
echo "Built RPM artifacts in $ROOT_DIR/dist"
