from pydantic import BaseModel, Field
from typing import Annotated

# Regex match to (hopefully) prevent weird CLI injection issues
Library = Annotated[str, Field(pattern=r"^[a-zA-Z ]*$")]


class Sketch(BaseModel):
    source_code: str
    # TODO: make this an enum with supported board types
    board: str
    libraries: list[Library]
