# Build From Clone

This repository does not store generated installers, model weights, virtual
environments, or build output. A fresh clone must build those locally.

## Clone

Replace the URL with the actual repository URL:

```sh
git clone <repo-url>
cd stt
```

If the folder has a different name, run all commands from that cloned project
root.

## Windows: Run From Source

Requirements:

- Windows 10/11
- Python 3.11
- NVIDIA GPU for the default GPU profile, or CPU profile for CPU-only use

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Run:

```powershell
.\.venv\Scripts\python.exe -m local_dictation run
```

## Windows: Build Installable ZIPs

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\create_distribution_zip.ps1 -Edition gpu
powershell -ExecutionPolicy Bypass -File .\packaging\windows\create_distribution_zip.ps1 -Edition cpu
```

Outputs:

```text
dist\releases\LocalWhisperDictation-gpu.zip
dist\releases\LocalWhisperDictation-cpu.zip
```

Give one of those ZIP files to a Windows user. They extract it and run:

```text
Run Local Whisper Dictation.bat
```

## Windows: Current-User Install

GPU edition:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -Edition gpu -StartWithWindows
```

CPU edition:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\build.ps1
powershell -ExecutionPolicy Bypass -File .\packaging\windows\install_current_user.ps1 -Edition cpu
```

Uninstall:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\windows\uninstall_current_user.ps1
```

## Ubuntu/Debian: Build `.deb`

Run on Ubuntu or Debian from the cloned project root:

```sh
sudo apt update
sudo apt install -y python3 python3-venv python3-pip dpkg-dev
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_deb.sh
```

Output:

```text
dist/local-whisper-dictation_0.1.0_amd64.deb
```

Give that `.deb` file to an Ubuntu/Debian user.

Install:

```sh
sudo apt install ./dist/local-whisper-dictation_0.1.0_amd64.deb
```

Validate:

```sh
./packaging/linux/validate_ubuntu.sh
local-dictation smoke-model --model tiny --compute-type int8
local-dictation run
```

Remove:

```sh
sudo apt remove local-whisper-dictation
```

Ubuntu details are also in [docs/UBUNTU.md](docs/UBUNTU.md).

## Fedora: Build `.rpm`

Run on Fedora from the cloned project root:

```sh
sudo dnf install -y python3 python3-pip rpm-build
./packaging/linux/build_wheelhouse.sh
./packaging/linux/build_rpm.sh
```

Expected output:

```text
dist/local-whisper-dictation-0.1.0-1*.noarch.rpm
```

Install:

```sh
sudo dnf install ./dist/local-whisper-dictation-0.1.0-1*.noarch.rpm
```

## Model Notes

Model weights are not committed to Git.

Default packaged profiles:

```text
Windows GPU: large-v3, cuda, float16
Windows CPU: small.en, cpu, int8
Ubuntu/Debian: small.en, cpu, int8
```

The first transcription may download the configured faster-whisper model unless
it is already cached or bundled in:

```text
models/faster-whisper-<model_name>
```

Examples:

```text
models/faster-whisper-small.en
models/faster-whisper-large-v3
```

Download a model into the project-local `models` folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\download_model.ps1 -ModelName small.en
```

On Linux, faster-whisper can also download models into its normal Hugging Face
cache on first use.

## Verification

Before distributing a build, run:

```powershell
.\.venv\Scripts\python.exe -m compileall -q src tests
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

On Linux, after installing the package:

```sh
local-dictation --version
local-dictation print-config
local-dictation diagnostics
```
