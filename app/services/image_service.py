#!/usr/bin/env python3
"""Validate Image Data against Image Schema"""

from app.schemas import ImageSchema
from app.database import images_collection  # Assume MongoDB setup

def save_image(image_data: bytes):
    validated_image = ImageSchema(image=image_data)
    images_collection.insert_one(validated_image.dict())
