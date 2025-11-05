"""
Resource Data Access Layer (DAL)
Handles all database operations for Resource model with CRUD functions.
"""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.extensions import db
from src.models import Resource


class ResourceDAL:
    """Data Access Layer for Resource model."""

    @staticmethod
    def create_resource(name: str, location: str, resource_type: str, creator_id: int,
                       description: str = None, capacity: int = None, status: str = 'published',
                       is_available: bool = True, available_from: datetime = None,
                       available_until: datetime = None) -> Resource:
        """
        Create a new resource.

        Args:
            name (str): Resource name
            location (str): Physical or virtual location
            resource_type (str): Type of resource (room, equipment, service, etc.)
            creator_id (int): ID of user creating the resource
            description (str): Resource description. Optional.
            capacity (int): Maximum capacity. Optional.
            status (str): Publication status - 'draft', 'published', 'archived'. Default: 'published'
            is_available (bool): Availability flag. Default: True
            available_from (datetime): Start of availability window. Optional.
            available_until (datetime): End of availability window. Optional.

        Returns:
            Resource: Created resource object

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            resource = Resource(
                name=name,
                location=location,
                resource_type=resource_type,
                creator_id=creator_id,
                description=description,
                capacity=capacity,
                status=status,
                is_available=is_available,
                available_from=available_from,
                available_until=available_until
            )
            db.session.add(resource)
            db.session.commit()
            return resource
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error creating resource: {str(e)}")

    @staticmethod
    def get_resource_by_id(resource_id: int) -> Resource:
        """
        Get resource by ID.

        Args:
            resource_id (int): Resource's primary key

        Returns:
            Resource: Resource object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return db.session.get(Resource, resource_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching resource by ID: {str(e)}")

    @staticmethod
    def get_resources_by_creator(creator_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get resources by creator ID.

        Args:
            creator_id (int): ID of resource creator
            limit (int): Maximum number of resources to return. Optional.
            offset (int): Number of resources to skip. Default: 0

        Returns:
            list: List of Resource objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Resource.query.filter_by(creator_id=creator_id).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching resources by creator: {str(e)}")

    @staticmethod
    def get_resources_by_type(resource_type: str, limit: int = None, offset: int = 0) -> list:
        """
        Get resources by type.

        Args:
            resource_type (str): Type of resource to filter by
            limit (int): Maximum number of resources to return. Optional.
            offset (int): Number of resources to skip. Default: 0

        Returns:
            list: List of Resource objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Resource.query.filter_by(resource_type=resource_type).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching resources by type: {str(e)}")

    @staticmethod
    def get_resources_by_status(status: str, limit: int = None, offset: int = 0) -> list:
        """
        Get resources by status.

        Args:
            status (str): Status to filter by - 'draft', 'published', 'archived'
            limit (int): Maximum number of resources to return. Optional.
            offset (int): Number of resources to skip. Default: 0

        Returns:
            list: List of Resource objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Resource.query.filter_by(status=status).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching resources by status: {str(e)}")

    @staticmethod
    def get_available_resources(limit: int = None, offset: int = 0) -> list:
        """
        Get available resources (is_available=True and status='published').

        Args:
            limit (int): Maximum number of resources to return. Optional.
            offset (int): Number of resources to skip. Default: 0

        Returns:
            list: List of available Resource objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Resource.query.filter_by(
                is_available=True,
                status='published'
            ).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching available resources: {str(e)}")

    @staticmethod
    def get_all_resources(limit: int = None, offset: int = 0) -> list:
        """
        Get all resources with optional pagination.

        Args:
            limit (int): Maximum number of resources to return. Optional.
            offset (int): Number of resources to skip. Default: 0

        Returns:
            list: List of Resource objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Resource.query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching resources: {str(e)}")

    @staticmethod
    def search_resources(search_term: str, limit: int = None, offset: int = 0) -> list:
        """
        Search resources by name or description.

        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of resources to return. Optional.
            offset (int): Number of resources to skip. Default: 0

        Returns:
            list: List of matching Resource objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Resource.query.filter(
                (Resource.name.ilike(f"%{search_term}%")) |
                (Resource.description.ilike(f"%{search_term}%"))
            ).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error searching resources: {str(e)}")

    @staticmethod
    def update_resource(resource_id: int, **kwargs) -> Resource:
        """
        Update resource by ID.

        Args:
            resource_id (int): Resource's primary key
            **kwargs: Fields to update (name, description, location, resource_type,
                     capacity, status, is_available, available_from, available_until)

        Returns:
            Resource: Updated resource object

        Raises:
            ValueError: If resource not found
            SQLAlchemyError: For database errors
        """
        try:
            resource = db.session.get(Resource, resource_id)
            if not resource:
                raise ValueError(f"Resource with ID {resource_id} not found")

            allowed_fields = {
                'name', 'description', 'location', 'resource_type',
                'capacity', 'status', 'is_available', 'available_from', 'available_until'
            }
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(resource, key, value)

            db.session.commit()
            return resource
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating resource: {str(e)}")

    @staticmethod
    def publish_resource(resource_id: int) -> Resource:
        """
        Publish a resource (change status to 'published').

        Args:
            resource_id (int): Resource's primary key

        Returns:
            Resource: Updated resource object

        Raises:
            ValueError: If resource not found
            SQLAlchemyError: For database errors
        """
        try:
            resource = db.session.get(Resource, resource_id)
            if not resource:
                raise ValueError(f"Resource with ID {resource_id} not found")

            resource.status = 'published'
            db.session.commit()
            return resource
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error publishing resource: {str(e)}")

    @staticmethod
    def archive_resource(resource_id: int) -> Resource:
        """
        Archive a resource (change status to 'archived').

        Args:
            resource_id (int): Resource's primary key

        Returns:
            Resource: Updated resource object

        Raises:
            ValueError: If resource not found
            SQLAlchemyError: For database errors
        """
        try:
            resource = db.session.get(Resource, resource_id)
            if not resource:
                raise ValueError(f"Resource with ID {resource_id} not found")

            resource.status = 'archived'
            db.session.commit()
            return resource
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error archiving resource: {str(e)}")

    @staticmethod
    def delete_resource(resource_id: int) -> bool:
        """
        Delete resource by ID.

        Args:
            resource_id (int): Resource's primary key

        Returns:
            bool: True if deletion successful, False if resource not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            resource = db.session.get(Resource, resource_id)
            if not resource:
                return False

            db.session.delete(resource)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting resource: {str(e)}")

    @staticmethod
    def resource_count() -> int:
        """
        Get total count of resources.

        Returns:
            int: Total number of resources

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return Resource.query.count()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error counting resources: {str(e)}")
