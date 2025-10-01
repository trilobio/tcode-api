"""TCode API types for type annotation shorthand."""

Tags = list[str]
NamedTags = dict[str, str | int | float | bool]

UnsanitizedFloat = float | int | str

Matrix = list[list[float]]

CommandID = str  # Identifier specifically for TCode command
