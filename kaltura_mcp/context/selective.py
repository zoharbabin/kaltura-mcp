"""
Selective context strategy for context management.
"""


class SelectiveContextStrategy:
    """Strategy for selecting specific fields from data."""

    def apply(self, data, **kwargs):
        """Apply selective context to the data.

        Args:
            data: The data to filter
            **kwargs: Additional parameters
                fields: The fields to include

        Returns:
            dict: The filtered data
        """
        fields = kwargs.get("fields", None)

        # Apply selective context logic here
        if not fields:
            # Return data as is if no fields specified
            return data

        if isinstance(data, dict):
            # Filter dictionary fields
            result = {}
            for field in fields:
                # Handle field name mapping (e.g., createdAt -> created_at)
                if field in data:
                    result[field] = data[field]
                elif field == "created_at" and "createdAt" in data:
                    result["created_at"] = data["createdAt"]
                elif field == "updated_at" and "updatedAt" in data:
                    result["updated_at"] = data["updatedAt"]
                elif field == "screen_name" and "screenName" in data:
                    result["screen_name"] = data["screenName"]
            return result
        elif hasattr(data, "__dict__"):
            # Handle objects by converting to dict first
            obj_dict = {}
            for field in fields:
                # Handle field name mapping (e.g., createdAt -> created_at)
                if hasattr(data, field):
                    obj_dict[field] = getattr(data, field)
                elif field == "created_at" and hasattr(data, "createdAt"):
                    obj_dict["created_at"] = data.createdAt
                elif field == "updated_at" and hasattr(data, "updatedAt"):
                    obj_dict["updated_at"] = data.updatedAt
                elif field == "screen_name" and hasattr(data, "screenName"):
                    obj_dict["screen_name"] = data.screenName
            return obj_dict
        else:
            # Return data as is if we can't filter
            return data
