# TCode API Documentation²

## Build the Documentation

1. Run the `make html` command in the appropriate directory using `uv`:

```
cd tcode-api/docs
uv run make html
```

2. Open `tcode-api/docs/_build/html/index.html` in your browser.

## Documentation Plugins

### autodoc-pydantic

`autodoc`'s default documentation for Pydantic models is trash, so we use a Sphinx extension to make it better.

**Link:** https://autodoc-pydantic.readthedocs.io/en/stable/users/usage.html

#### Before

```
class tcode_api.api.commands.ADD_LABWARE(**data)

Resolve the given descriptor to a labware on the fleet and assign it the given id.

model_config: ClassVar[ConfigDict] = {'extra': 'ignore', 'strict': True}

    Configuration for the model, should be a dictionary conforming to [ConfigDict][pydantic.config.ConfigDict].
```

#### After

```
pydantic model tcode_api.api.commands.ADD_LABWARE

Resolve the given descriptor to a labware on the fleet and assign it the given id.

> Show JSON schema

Config:

        strict: bool = True

        extra: str = ignore

Fields:

        descriptor (tcode_api.api.labware.LidDescriptor | tcode_api.api.labware.PipetteTipBoxDescriptor | tcode_api.api.labware.TrashDescriptor | tcode_api.api.labware.TubeHolderDescriptor | tcode_api.api.labware.WellPlateDescriptor)

        id (str)

        type (Literal['ADD_LABWARE'])

field descriptor: Annotated[LidDescriptor | PipetteTipBoxDescriptor | TrashDescriptor | TubeHolderDescriptor | WellPlateDescriptor] [Required]

field id: str [Required]

field type: Literal['ADD_LABWARE'] = 'ADD_LABWARE'
```
