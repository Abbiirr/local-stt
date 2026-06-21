import os
import sys

from local_dictation.single_instance import acquire_lock, mark_bootstrap_lock_held, should_lock_for_argv


_INSTANCE_LOCK_HANDLE = None

if should_lock_for_argv(sys.argv):
    _INSTANCE_LOCK_HANDLE, _already_running = acquire_lock()
    if _already_running:
        os._exit(0)
    mark_bootstrap_lock_held()

from local_dictation.__main__ import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
