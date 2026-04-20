import pathlib


class Rewriter:
    """Modify a file one line at a time."""

    def __init__(self, file: str | pathlib.Path):
        self.file = pathlib.Path(file)
        self._lines = self.file.read_text().splitlines()
        self._first_line_index = 0
        self._indent = ''

    def set_indent(self, length: int):
        """Set the number of spaces for indentation."""
        self._indent = ' ' * length

    def fwd(self, prefix: str, *, change: str | None = None, remove_line: bool = False):
        """Set the current location to the next line that matches a prefix."""
        # To help make calling code more readable, it's important that the name of this method has
        # three characters, to align with add(). It's also important that 'prefix' and 'change'
        # have the same number of characters.
        prefix_with_indent = self._indent + prefix
        for line_index in range(self._first_line_index, len(self._lines)):
            line = self._lines[line_index]
            if line.startswith(prefix_with_indent):
                if remove_line:
                    del self._lines[line_index]
                    self._first_line_index = line_index
                    return
                if change is not None:
                    self._lines[line_index] = (
                        self._indent + change + line[len(prefix_with_indent) :]
                    )
                self._first_line_index = line_index + 1
                return
        raise ValueError('no matching line')

    def add(self, new: str, *, offset: int = 0):
        """Insert lines at the current location."""
        new_lines = new.split('\n')
        for new_line in new_lines:
            self._lines.insert(self._first_line_index + offset, self._indent + new_line)
            self._first_line_index += 1

    def save(self):
        """Save the modified file."""
        lines = self._lines + ['']
        self.file.write_text('\n'.join(lines))
