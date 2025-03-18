"""
Summarization strategy for context management.
"""


class SummarizationStrategy:
    """Strategy for summarizing data."""

    def apply(self, data, **kwargs):
        """Apply summarization to the data.

        Args:
            data: The data to summarize
            **kwargs: Additional parameters
                max_length: The maximum length of the summary

        Returns:
            dict: The summarized data
        """
        max_length = kwargs.get("max_length", 100)

        # Apply summarization logic here
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if isinstance(value, str) and len(value) > max_length:
                    # Truncate to max_length - 3 to account for the ellipsis
                    result[key] = value[: max_length - 3] + "..."
                else:
                    result[key] = value
            return result
        elif hasattr(data, "__dict__"):
            # Handle objects by converting to dict first
            obj_dict = {}
            for key, value in data.__dict__.items():
                if isinstance(value, str) and len(value) > max_length:
                    # Truncate to max_length - 3 to account for the ellipsis
                    obj_dict[key] = value[: max_length - 3] + "..."
                else:
                    obj_dict[key] = value
            return obj_dict
        else:
            # Return data as is if we can't summarize
            return data
