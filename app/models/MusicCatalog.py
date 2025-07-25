from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MusicCatalog(BaseModel):
    id: int = Field(
        default=None,
        ge=1,
        description="Auto-generated ID"
    )

    app: Optional['str'] = Field(
        default=None
    )

    review: Optional['str'] = Field(
        default=None
    )

    rating: Optional['float'] = Field(
        default=None
    )

    version: Optional['str'] = Field(
        default=None
    )

    review_date: Optional['date'] = Field(
        default=None
    )