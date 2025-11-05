"""
User Data Access Layer (DAL)
Handles all database operations for User model with CRUD functions.
"""

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.extensions import db
from src.models import User


class UserDAL:
    """Data Access Layer for User model."""

    @staticmethod
    def create_user(username: str, email: str, full_name: str, password: str,
                    role: str = 'student', department: str = None, profile_image: str = None) -> User:
        """
        Create a new user.

        Args:
            username (str): Unique username for login
            email (str): Unique email address
            full_name (str): User's full name
            password (str): Plain text password (will be hashed)
            role (str): User role - 'student', 'staff', or 'admin'. Default: 'student'
            department (str): User's department. Optional.
            profile_image (str): Path to profile image. Optional.

        Returns:
            User: Created user object

        Raises:
            IntegrityError: If username or email already exists
            SQLAlchemyError: For other database errors
        """
        try:
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                department=department,
                profile_image=profile_image
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            raise IntegrityError(
                "User with this username or email already exists",
                e.orig,
                e.orig
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error creating user: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """
        Get user by ID.

        Args:
            user_id (int): User's primary key

        Returns:
            User: User object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return db.session.get(User, user_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching user by ID: {str(e)}")

    @staticmethod
    def get_user_by_username(username: str) -> User:
        """
        Get user by username.

        Args:
            username (str): Username to search for

        Returns:
            User: User object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            # Use explicit db.session.query instead of User.query for better compatibility
            user = db.session.query(User).filter(User.username == username).first()
            return user
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching user by username: {str(e)}")

    @staticmethod
    def get_user_by_email(email: str) -> User:
        """
        Get user by email.

        Args:
            email (str): Email to search for

        Returns:
            User: User object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            # Use explicit db.session.query instead of User.query for better compatibility
            user = db.session.query(User).filter(User.email == email).first()
            return user
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching user by email: {str(e)}")

    @staticmethod
    def get_all_users(limit: int = None, offset: int = 0) -> list:
        """
        Get all users with optional pagination.

        Args:
            limit (int): Maximum number of users to return. Optional.
            offset (int): Number of users to skip. Default: 0

        Returns:
            list: List of User objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = User.query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching users: {str(e)}")

    @staticmethod
    def get_users_by_role(role: str, limit: int = None, offset: int = 0) -> list:
        """
        Get users by role.

        Args:
            role (str): Role to filter by - 'student', 'staff', or 'admin'
            limit (int): Maximum number of users to return. Optional.
            offset (int): Number of users to skip. Default: 0

        Returns:
            list: List of User objects with specified role

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = User.query.filter_by(role=role).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching users by role: {str(e)}")

    @staticmethod
    def update_user(user_id: int, **kwargs) -> User:
        """
        Update user by ID.

        Args:
            user_id (int): User's primary key
            **kwargs: Fields to update (email, full_name, department, profile_image, role, is_active)

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found
            IntegrityError: If unique constraint violated
            SQLAlchemyError: For other database errors
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            allowed_fields = {'email', 'full_name', 'department', 'profile_image', 'role', 'is_active'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(user, key, value)

            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            raise IntegrityError("Update violates unique constraint", e.orig, e.orig)
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating user: {str(e)}")

    @staticmethod
    def update_user_password(user_id: int, new_password: str) -> User:
        """
        Update user password.

        Args:
            user_id (int): User's primary key
            new_password (str): New plain text password

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found
            SQLAlchemyError: For database errors
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            user.set_password(new_password)
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating password: {str(e)}")

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Delete user by ID.

        Args:
            user_id (int): User's primary key

        Returns:
            bool: True if deletion successful, False if user not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                return False

            db.session.delete(user)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting user: {str(e)}")

    @staticmethod
    def user_count() -> int:
        """
        Get total count of users.

        Returns:
            int: Total number of users

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return User.query.count()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error counting users: {str(e)}")

    @staticmethod
    def deactivate_user(user_id: int) -> User:
        """
        Deactivate a user (soft delete).

        Args:
            user_id (int): User's primary key

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found
            SQLAlchemyError: For database errors
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            user.is_active = False
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deactivating user: {str(e)}")

    @staticmethod
    def activate_user(user_id: int) -> User:
        """
        Activate a deactivated user.

        Args:
            user_id (int): User's primary key

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found
            SQLAlchemyError: For database errors
        """
        try:
            user = db.session.get(User, user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            user.is_active = True
            db.session.commit()
            return user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error activating user: {str(e)}")
