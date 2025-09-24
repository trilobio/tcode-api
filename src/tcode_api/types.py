"""TCode API types for type annotation shorthand."""

Tags = list[str]
NamedTags = dict[str, str | int | float | bool]

UnsanitizedFloat = float | int | str

CommandID = str  # Identifier specifically for TCode command
