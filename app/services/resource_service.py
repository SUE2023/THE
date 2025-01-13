#!/usr/bin/env python3
"""" Service for resources"""


class ResourceService:
    """Service to manage resources in SQLite and MongoDB."""

    @staticmethod
    def create_resource(data: dict, image: bytes = None):
        # Save image to MongoDB
        image_id = None
        if image:
            result = images_collection.insert_one({"image": image})
            image_id = str(result.inserted_id)

        # Save resource to SQLite
        resource = Resource(
            user_id=data["user_id"],
            title=data["title"],
            description=data.get("description"),
            image_id=image_id,
        )
        db.session.add(resource)
        db.session.commit()
        return resource

    @staticmethod
    def get_resource(resource_id: int):
        # Fetch resource from SQLite
        resource = Resource.query.get(resource_id)
        if not resource:
            return None

        # Fetch image from MongoDB
        image = None
        if resource.image_id:
            image_doc = images_collection.find_one({"_id": ObjectId(resource.image_id)})
            image = image_doc["image"] if image_doc else None

        # Combine data
        resource_data = resource.to_dict()
        resource_data["image"] = image
        return resource_data
