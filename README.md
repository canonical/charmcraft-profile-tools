This repo contains tools for maintaining the `kubernetes` and `machine` profiles of [Charmcraft](https://github.com/canonical/charmcraft). The tools are primarily intended to be used by the Charm Tech team at Canonical.

In the Charmcraft source, profiles are stored as .j2 template files. For example, [charm.py.j2](https://github.com/canonical/charmcraft/blob/main/charmcraft/templates/init-kubernetes/src/charm.py.j2). This enables `charmcraft init` to fill in the charm name and other details, but testing the profiles can be awkward.

**In this README**

- [TL;DR: Update the profiles in a single shot](#tldr-update-the-profiles-in-a-single-shot)
- [Generate charms for testing](#generate-charms-for-testing)
    - [Integration tests](#integration-tests)
    - [kubernetes-extra](#kubernetes-extra)
- [Update the uv.lock templates](#update-the-uvlock-templates)

## TL;DR: Update the profiles in a single shot

> [!TIP]
> Read this section if all you want to do is open a PR to Charmcraft and get on with your day!

You'll need the Charmcraft source and [uv](https://docs.astral.sh/uv/).

After editing .j2 files in the Charmcraft source, run the following commands at the root of the Charmcraft source:

```text
make setup
uv run https://raw.githubusercontent.com/canonical/charmcraft-profile-tools/refs/heads/main/inplace.py
```

The Python script:

1. Clones this repo into the Charmcraft source
2. Initializes a Kubernetes charm and a machine charm
3. Lints each charm and runs its unit tests
4. Locks the dependencies of each charm and updates `uv.lock.j2`

If everything went well, commit your changes and open your PR 😌

## Generate charms for testing

You'll need:

- The Charmcraft source. We'll assume this is located at `~/charmcraft`.
- A virtual environment in the Charmcraft source. To create one, run `make setup` in the Charmcraft source.
- [just](https://just.systems/man/en/), [uv](https://docs.astral.sh/uv/), and [tox](https://tox.wiki/en/). To install tox, run `uv tool install tox --with tox-uv`.

After editing .j2 files in the Charmcraft source, run the following command in this repo:

```text
CHARMCRAFT_DIR=~/charmcraft just init
```

This initializes a Kubernetes charm in the `kubernetes` directory and a machine charm in the `machine` directory. If you only want one of the charms, use `just kubernetes` or `just machine` instead of `just init`.

You can test the charms as normal using tox. Alternatively, initialize the charms and immediately test them:

```text
CHARMCRAFT_DIR=~/charmcraft just init lint,unit
```

The list of environments after `just init` is passed to `tox -e <environments>` for each charm. This also works with `just kubernetes` and `just machine`.

### Integration tests

Integration tests require a Juju controller. You can use [Concierge](https://github.com/canonical/concierge) to bootstrap a Juju controller.

> [!IMPORTANT]
> Don't run integration tests using `just ... integration`. Instead, in each directory, run `charmcraft pack` followed by `tox -e integration`.

The machine charm's integration tests should pass. The charm goes active without installing a workload.

The Kubernetes charm's integration tests should fail because Juju tries to deploy the charm alongside a placeholder container image.

### kubernetes-extra

To generate a Kubernetes charm that passes integration tests, make sure you've initialized a Kubernetes charm (as above), then run:

```text
just kubernetes-extra
```

This copies `kubernetes` to a directory called `kubernetes-extra`, then replaces the placeholder parts of the charm by real configuration/code. For details, see [.implement/kubernetes-extra.py](.implement/kubernetes-extra.py).

To generate the charm and immediately test it:

```text
just kubernetes-extra lint,unit
```

To run the charm's integration tests:

```text
cd kubernetes-extra
charmcraft pack
tox -e integration
```

## Update the uv.lock templates

If you change the dependencies of the Charmcraft profiles, you'll need to update `uv.lock.j2` for each profile.

Make sure you've initialized a Kubernetes charm and a machine charm (see [Generate charms for testing](#generate-charms-for-testing)). Then run `just lock`. This locks the dependencies of each charm and generates template files:

- `.templates/init-kubernetes/uv.lock.j2`
- `.templates/init-machine/uv.lock.j2`

You can copy these files to the Charmcraft source. Alternatively, run `CHARMCRAFT_DIR=~/charmcraft just lock` to generate the `uv.lock.j2` files and copy them to the Charmcraft source.

If you only want one of the files, use `just lock-kubernetes` or `just lock-machine` instead of `just lock`.
