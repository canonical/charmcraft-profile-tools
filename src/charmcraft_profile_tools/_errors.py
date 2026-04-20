NOT_FROM_SOURCE = """Error: Not running from source

Use 'uv run <command>' in a clone of charmcraft-profile-tools."""

NOT_INSIDE_CHARMCRAFT = """Error: Your clone of charmcraft-profile-tools is not inside the Charmcraft source

Set CHARMCRAFT_DIR to the location of the Charmcraft source."""

NO_KUBERNETES = """Error: No 'kubernetes' charm in your clone of charmcraft-profile-tools

To generate the 'kubernetes' charm, use 'uv run kubernetes'."""
