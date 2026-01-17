"""
Query Parameter Processing for Filtering, Sorting, and Pagination
Provides utilities for parsing and applying query filters to SQLAlchemy queries.
"""

from datetime import datetime
from utils.errors import ValidationError


class QueryFilter:
    """
    Helper class for processing query parameters.
    Supports filtering, sorting, and pagination.
    """

    # Valid fields for sorting per resource type
    VALID_SORT_FIELDS = {
        'medicines': ['name', 'form', 'dosage', 'created_at'],
        'declarations': ['status', 'created_at', 'updated_at', 'citizen_id'],
        'propositions': ['status', 'created_at', 'updated_at'],
        'supplies': ['name', 'condition', 'quantity', 'price', 'created_at', 'updated_at'],
    }

    # Valid filter fields per resource type
    VALID_FILTER_FIELDS = {
        'medicines': ['name', 'status', 'created_at'],
        'declarations': ['status', 'created_at'],
        'propositions': ['status', 'created_at'],
        'supplies': ['condition', 'is_for_sale', 'created_at'],
    }

    @staticmethod
    def parse_pagination(request):
        """
        Parse pagination parameters from request.

        Query params:
        - page: Page number (default: 1)
        - limit: Items per page (default: 10, max: 100)

        Returns:
            tuple: (page, limit, offset)
        
        Raises:
            ValidationError: If parameters are invalid
        """
        try:
            page = request.args.get('page', default=1, type=int)
            limit = request.args.get('limit', default=10, type=int)

            # Validate ranges
            if page < 1:
                raise ValidationError(
                    'Page must be >= 1',
                    error_code='VAL_004',
                    fields={'page': 'Page must be >= 1'}
                )
            if limit < 1 or limit > 100:
                raise ValidationError(
                    'Limit must be between 1 and 100',
                    error_code='VAL_004',
                    fields={'limit': 'Limit must be between 1 and 100'}
                )

            offset = (page - 1) * limit
            return page, limit, offset

        except ValueError as e:
            raise ValidationError(
                f'Invalid pagination parameter: {str(e)}',
                error_code='VAL_004'
            )

    @staticmethod
    def parse_sort(request, resource_type='medicines'):
        """
        Parse sorting parameters from request.

        Query params:
        - sort_by: Field name (from VALID_SORT_FIELDS)
        - order: 'asc' or 'desc' (default: 'asc')

        Returns:
            tuple: (sort_field, sort_order)
        
        Raises:
            ValidationError: If parameters are invalid
        """
        sort_by = request.args.get('sort_by', default='created_at')
        order = request.args.get('order', default='asc').lower()

        # Validate sort field
        valid_fields = QueryFilter.VALID_SORT_FIELDS.get(resource_type, [])
        if sort_by not in valid_fields:
            raise ValidationError(
                f"Invalid sort_by field: '{sort_by}'. Valid fields: {', '.join(valid_fields)}",
                error_code='VAL_004',
                fields={'sort_by': f"Must be one of: {', '.join(valid_fields)}"}
            )

        # Validate order
        if order not in ['asc', 'desc']:
            raise ValidationError(
                "Order must be 'asc' or 'desc'",
                error_code='VAL_004',
                fields={'order': "Must be 'asc' or 'desc'"}
            )

        return sort_by, order

    @staticmethod
    def parse_date(date_str):
        """
        Parse date string in YYYY-MM-DD format.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            datetime: Parsed datetime object (start of day)
        
        Raises:
            ValidationError: If date format is invalid
        """
        if not date_str:
            return None

        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d')
        except ValueError:
            raise ValidationError(
                f"Invalid date format: '{date_str}'. Use YYYY-MM-DD",
                error_code='VAL_006',
                fields={'date': "Format must be YYYY-MM-DD"}
            )

    @staticmethod
    def apply_filters_to_query(query, model, request, resource_type='medicines'):
        """
        Apply all filters from query parameters to SQLAlchemy query.

        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            request: Flask request object
            resource_type: Type of resource ('medicines', 'declarations', 'supplies')

        Returns:
            query: Filtered SQLAlchemy query

        Raises:
            ValidationError: If filter parameters are invalid
        """
        # Handle resource-specific filters
        if resource_type == 'medicines':
            # Filter by name (partial match)
            name_filter = request.args.get('name')
            if name_filter:
                query = query.filter(model.name.ilike(f"%{name_filter}%"))

            # Filter by created_from date
            created_from = request.args.get('created_from')
            if created_from:
                from_date = QueryFilter.parse_date(created_from)
                query = query.filter(model.created_at >= from_date)

            # Filter by created_to date
            created_to = request.args.get('created_to')
            if created_to:
                to_date = QueryFilter.parse_date(created_to)
                # End of day
                to_date = to_date.replace(hour=23, minute=59, second=59)
                query = query.filter(model.created_at <= to_date)

        elif resource_type == 'declarations':
            # Filter by status
            status_filter = request.args.get('status')
            if status_filter:
                query = query.filter(model.status == status_filter)

            # Filter by created_from date
            created_from = request.args.get('created_from')
            if created_from:
                from_date = QueryFilter.parse_date(created_from)
                query = query.filter(model.created_at >= from_date)

            # Filter by created_to date
            created_to = request.args.get('created_to')
            if created_to:
                to_date = QueryFilter.parse_date(created_to)
                to_date = to_date.replace(hour=23, minute=59, second=59)
                query = query.filter(model.created_at <= to_date)

        elif resource_type == 'supplies':
            # Filter by condition
            condition_filter = request.args.get('condition')
            if condition_filter:
                query = query.filter(model.condition == condition_filter)

            # Filter by is_for_sale
            is_for_sale = request.args.get('is_for_sale')
            if is_for_sale is not None:
                is_for_sale = is_for_sale.lower() in ['true', '1', 'yes']
                query = query.filter(model.is_for_sale == is_for_sale)

            # Filter by created_from date
            created_from = request.args.get('created_from')
            if created_from:
                from_date = QueryFilter.parse_date(created_from)
                query = query.filter(model.created_at >= from_date)

            # Filter by created_to date
            created_to = request.args.get('created_to')
            if created_to:
                to_date = QueryFilter.parse_date(created_to)
                to_date = to_date.replace(hour=23, minute=59, second=59)
                query = query.filter(model.created_at <= to_date)

            # Filter by active status (default: only active)
            show_inactive = request.args.get('show_inactive', 'false').lower() in ['true', '1', 'yes']
            if not show_inactive and hasattr(model, 'is_active'):
                query = query.filter(model.is_active == True)

        return query

    @staticmethod
    def apply_sorting(query, model, sort_field, sort_order='asc'):
        """
        Apply sorting to SQLAlchemy query.

        Args:
            query: SQLAlchemy query object
            model: SQLAlchemy model class
            sort_field: Field to sort by
            sort_order: 'asc' or 'desc' (default: 'asc')

        Returns:
            query: Sorted SQLAlchemy query
        """
        if not hasattr(model, sort_field):
            return query

        order_func = query.order_by if sort_order == 'asc' else query.order_by

        if sort_order == 'asc':
            query = query.order_by(getattr(model, sort_field).asc())
        else:
            query = query.order_by(getattr(model, sort_field).desc())

        return query

    @staticmethod
    def get_paginated_response(items, total_count, page, limit):
        """
        Build standardized paginated response.

        Args:
            items (list): List of items to return
            total_count (int): Total number of items (before pagination)
            page (int): Current page number
            limit (int): Items per page

        Returns:
            dict: Response with items and pagination metadata
        """
        total_pages = (total_count + limit - 1) // limit  # Ceiling division

        return {
            'data': items,
            'pagination': {
                'total_items': total_count,
                'page': page,
                'limit': limit,
                'total_pages': total_pages
            }
        }
