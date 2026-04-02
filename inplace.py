"""Run charmcraft-profile-tools from within the Charmcraft source."""

import os
import pathlib
import subprocess

OUR_CLONE = pathlib.Path() / "charmcraft-profile-tools" / "canonical-match-profiles"

# Make sure we have a clone of the charmcraft-profile-tools repo, with a new branch checked out
# in case we want to push the generated charms. Using https://github.com/dwilding/gimmegit.
if not OUR_CLONE.exists():
    subprocess.check_call(
        [
            "uvx",
            "gimmegit",
            "--allow-outer-repo",
            "canonical/charmcraft-profile-tools",
            "match-profiles",
        ]
    )

# Generate charms, check them, then update the uv.lock templates in the Charmcraft source.
env = os.environ.copy()
env["CHARMCRAFT_DIR"] = str(pathlib.Path.cwd())
subprocess.call(
    ["uvx", "--from", "rust-just", "just", "init", "lint,unit"], cwd=OUR_CLONE, env=env
)
subprocess.call(["uvx", "--from", "rust-just", "just", "lock"], cwd=OUR_CLONE, env=env)
