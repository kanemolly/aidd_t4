"""
Review Data Access Layer (DAL)
Handles all database operations for Review model with CRUD functions.
Includes rating aggregation and validation.
"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from src.extensions import db
from src.models import Review


class ReviewDAL:
    """Data Access Layer for Review model."""

    @staticmethod
    def create_review(user_id: int, resource_id: int, rating: int, comment: str = None, title: str = None) -> Review:
        """
        Create a new review.

        Args:
            user_id (int): ID of user writing the review
            resource_id (int): ID of resource being reviewed
            rating (int): Rating value - must be 1-5
            comment (str): Optional review comment
            title (str): Optional review title

        Returns:
            Review: Created review object

        Raises:
            ValueError: If rating is outside 1-5 range
            SQLAlchemyError: For database errors
        """
        try:
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")

            review = Review(
                reviewer_id=user_id,
                resource_id=resource_id,
                rating=rating,
                comment=comment,
                title=title
            )
            db.session.add(review)
            db.session.commit()
            return review
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error creating review: {str(e)}")

    @staticmethod
    def get_review_by_id(review_id: int) -> Review:
        """
        Get review by ID.

        Args:
            review_id (int): Review's primary key

        Returns:
            Review: Review object or None if not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return db.session.get(Review, review_id)
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching review by ID: {str(e)}")

    @staticmethod
    def get_user_reviews(user_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get all reviews written by a user.

        Args:
            user_id (int): ID of user
            limit (int): Maximum number of reviews to return. Optional.
            offset (int): Number of reviews to skip. Default: 0

        Returns:
            list: List of Review objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Review.query.filter_by(reviewer_id=user_id).order_by(Review.created_at.desc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching user reviews: {str(e)}")

    @staticmethod
    def get_resource_reviews(resource_id: int, limit: int = None, offset: int = 0) -> list:
        """
        Get all reviews for a specific resource.

        Args:
            resource_id (int): ID of resource
            limit (int): Maximum number of reviews to return. Optional.
            offset (int): Number of reviews to skip. Default: 0

        Returns:
            list: List of Review objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Review.query.filter_by(resource_id=resource_id).order_by(Review.created_at.desc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching resource reviews: {str(e)}")

    @staticmethod
    def get_reviews_by_rating(resource_id: int, rating: int, limit: int = None, offset: int = 0) -> list:
        """
        Get reviews for a resource filtered by rating.

        Args:
            resource_id (int): ID of resource
            rating (int): Rating to filter by (1-5)
            limit (int): Maximum number of reviews to return. Optional.
            offset (int): Number of reviews to skip. Default: 0

        Returns:
            list: List of Review objects

        Raises:
            ValueError: If rating is outside 1-5 range
            SQLAlchemyError: For database errors
        """
        try:
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")

            query = Review.query.filter_by(resource_id=resource_id, rating=rating).order_by(
                Review.created_at.desc()
            ).offset(offset)

            if limit:
                query = query.limit(limit)

            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching reviews by rating: {str(e)}")

    @staticmethod
    def get_all_reviews(limit: int = None, offset: int = 0) -> list:
        """
        Get all reviews with optional pagination.

        Args:
            limit (int): Maximum number of reviews to return. Optional.
            offset (int): Number of reviews to skip. Default: 0

        Returns:
            list: List of Review objects

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            query = Review.query.order_by(Review.created_at.desc()).offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error fetching reviews: {str(e)}")

    @staticmethod
    def get_average_rating(resource_id: int) -> float:
        """
        Get average rating for a resource.

        Args:
            resource_id (int): ID of resource

        Returns:
            float: Average rating (0.0 if no reviews)

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            result = db.session.query(func.avg(Review.rating)).filter_by(resource_id=resource_id).scalar()
            return float(result) if result else 0.0
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error calculating average rating: {str(e)}")

    @staticmethod
    def get_rating_distribution(resource_id: int) -> dict:
        """
        Get distribution of ratings for a resource.

        Args:
            resource_id (int): ID of resource

        Returns:
            dict: Dictionary with rating counts {1: count, 2: count, ..., 5: count}

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

            results = db.session.query(
                Review.rating,
                func.count(Review.id)
            ).filter_by(resource_id=resource_id).group_by(Review.rating).all()

            for rating, count in results:
                distribution[rating] = count

            return distribution
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error getting rating distribution: {str(e)}")

    @staticmethod
    def get_review_stats(resource_id: int) -> dict:
        """
        Get comprehensive review statistics for a resource.

        Args:
            resource_id (int): ID of resource

        Returns:
            dict: Dictionary with stats - average_rating, total_reviews, distribution

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            total_reviews = Review.query.filter_by(resource_id=resource_id).count()
            average_rating = ReviewDAL.get_average_rating(resource_id)
            distribution = ReviewDAL.get_rating_distribution(resource_id)

            return {
                'average_rating': round(average_rating, 2),
                'total_reviews': total_reviews,
                'distribution': distribution
            }
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error getting review stats: {str(e)}")

    @staticmethod
    def update_review(review_id: int, **kwargs) -> Review:
        """
        Update review by ID.

        Args:
            review_id (int): Review's primary key
            **kwargs: Fields to update (rating, comment)

        Returns:
            Review: Updated review object

        Raises:
            ValueError: If review not found or rating invalid
            SQLAlchemyError: For database errors
        """
        try:
            review = db.session.get(Review, review_id)
            if not review:
                raise ValueError(f"Review with ID {review_id} not found")

            if 'rating' in kwargs:
                if not (1 <= kwargs['rating'] <= 5):
                    raise ValueError("Rating must be between 1 and 5")

            allowed_fields = {'rating', 'comment'}
            for key, value in kwargs.items():
                if key in allowed_fields:
                    setattr(review, key, value)

            db.session.commit()
            return review
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error updating review: {str(e)}")

    @staticmethod
    def delete_review(review_id: int) -> bool:
        """
        Delete review by ID.

        Args:
            review_id (int): Review's primary key

        Returns:
            bool: True if deletion successful, False if review not found

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            review = db.session.get(Review, review_id)
            if not review:
                return False

            db.session.delete(review)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting review: {str(e)}")

    @staticmethod
    def delete_resource_reviews(resource_id: int) -> int:
        """
        Delete all reviews for a resource.

        Args:
            resource_id (int): ID of resource

        Returns:
            int: Number of reviews deleted

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            count = Review.query.filter_by(resource_id=resource_id).count()
            Review.query.filter_by(resource_id=resource_id).delete()
            db.session.commit()
            return count
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Error deleting resource reviews: {str(e)}")

    @staticmethod
    def review_count() -> int:
        """
        Get total count of reviews.

        Returns:
            int: Total number of reviews

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return Review.query.count()
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error counting reviews: {str(e)}")

    @staticmethod
    def user_reviewed_resource(user_id: int, resource_id: int) -> bool:
        """
        Check if a user has already reviewed a resource.

        Args:
            user_id (int): ID of user
            resource_id (int): ID of resource

        Returns:
            bool: True if user has reviewed, False otherwise

        Raises:
            SQLAlchemyError: For database errors
        """
        try:
            return Review.query.filter_by(reviewer_id=user_id, resource_id=resource_id).count() > 0
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error checking user review: {str(e)}")
