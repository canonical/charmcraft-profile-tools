[private]
default:
  @just --list

[doc("Initialize a Kubernetes charm. CHARMCRAFT_DIR must be set")]
kubernetes *uv_lock_args:
  @.scripts/check_charmcraft_root.sh
  @rm -rf kubernetes
  uv run --directory $CHARMCRAFT_DIR --python 3.10 --no-dev \
    charmcraft init \
    --project-dir "{{justfile_directory()}}/kubernetes" \
    --profile kubernetes \
    --name my-application \
    --author Charmer
  uv lock --directory kubernetes --python 3.10 {{uv_lock_args}}
  cp "{{justfile_directory()}}/kubernetes/uv.lock" "$CHARMCRAFT_DIR/charmcraft/templates/init-kubernetes/uv.lock.j2"
  sed -i 's/my-application/{{{{ name }}/g' "$CHARMCRAFT_DIR/charmcraft/templates/init-kubernetes/uv.lock.j2"
  uvx --directory kubernetes --python 3.10 \
    --with tox-uv tox -e lint,unit

[doc("Initialize a machine charm. CHARMCRAFT_DIR must be set")]
machine *uv_lock_args:
  @.scripts/check_charmcraft_root.sh
  @rm -rf machine
  uv run --directory $CHARMCRAFT_DIR --python 3.10 --no-dev \
    charmcraft init \
    --project-dir "{{justfile_directory()}}/machine" \
    --profile machine \
    --name my-application \
    --author Charmer
  uv lock --directory machine --python 3.10 {{uv_lock_args}}
  cp "{{justfile_directory()}}/machine/uv.lock" "$CHARMCRAFT_DIR/charmcraft/templates/init-machine/uv.lock.j2"
  sed -i 's/my-application/{{{{ name }}/g' "$CHARMCRAFT_DIR/charmcraft/templates/init-machine/uv.lock.j2"
  uvx --directory machine --python 3.10 \
    --with tox-uv tox -e lint,unit

[doc("Implement a more complete version of the Kubernetes charm")]
kubernetes-extra:
  @test -d kubernetes
  @rm -rf kubernetes-extra
  @cp -r kubernetes kubernetes-extra
  @cd kubernetes-extra && rm -rf .coverage .ruff_cache .tox .venv
  uv run --directory {{justfile_directory()}}/kubernetes-extra \
    --project {{justfile_directory()}}/.implement \
    {{justfile_directory()}}/.implement/kubernetes-extra.py
  uvx --directory {{justfile_directory()}}/kubernetes-extra --python 3.10 \
    --with tox-uv tox -e format,lint,unit
