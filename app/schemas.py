#!/usr/bin/env python3
""" Schema Definition"""

from pydantic import BaseModel


class ImageSchema(BaseModel):
    image: bytes
