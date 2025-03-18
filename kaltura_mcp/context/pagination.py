"""
Pagination strategy for context management.
"""


class PaginationStrategy:
    """Strategy for paginating data."""

    def apply(self, data, **kwargs):
        """Apply pagination to the data.

        Args:
            data: The data to paginate
            **kwargs: Additional parameters
                page_size: The number of items per page
                page: The page number (1-based)

        Returns:
            dict: The paginated data
        """
        page_size = kwargs.get("page_size", 10)
        page = kwargs.get("page", 1)

        # Apply pagination logic here
        if hasattr(data, "objects") and hasattr(data, "totalCount"):
            # Handle Kaltura API response objects
            total = data.totalCount
            items = data.objects
        elif isinstance(data, dict) and "objects" in data and "totalCount" in data:
            # Handle dictionary with objects and totalCount
            total = data["totalCount"]
            items = data["objects"]
        elif isinstance(data, list):
            # Handle simple list
            total = len(data)
            items = data
        else:
            # Return data as is if we can't paginate
            return data

        # Calculate pagination
        start_index = (page - 1) * page_size
        end_index = min(start_index + page_size, total)

        # Get paginated items
        if isinstance(items, list):
            paginated_items = items[start_index:end_index]
        else:
            # If we can't slice, return all items
            paginated_items = items

        # Return paginated result
        total_pages = (total + page_size - 1) // page_size
        return {
            "items": paginated_items,
            "entries": paginated_items,  # For backward compatibility
            "totalCount": total,
            "total_count": total,  # For backward compatibility
            "pageSize": page_size,
            "page_size": page_size,  # For backward compatibility
            "pageIndex": page,
            "page": page,  # For backward compatibility
            "totalPages": total_pages,
            "total_pages": total_pages,  # For backward compatibility
        }
