# Add Pydantic Type Safety - VERYLARGE (8 hours)

**Complexity**: High  
**Impact**: Very High - Runtime validation, better developer experience, and API safety  
**Time Estimate**: 8 hours  
**Dependencies**: Tool registry pattern (optional for enhanced registry features)

## Problem
The current system lacks:
- Runtime input validation beyond basic checks
- Type safety for API requests and responses
- Consistent data serialization/deserialization
- Clear data models for documentation
- Validation error handling with detailed feedback
- IDE support with auto-completion

## Solution
Implement comprehensive Pydantic models for:
- Tool input validation with detailed schemas
- Response formatting with type safety
- Configuration validation
- Error responses with structured feedback
- API documentation generation
- IDE support through type hints

## Implementation Steps

### 1. Install and Configure Pydantic (15 minutes)
**Update `pyproject.toml`:**
```toml
dependencies = [
    # ... existing dependencies
    "pydantic>=2.5.0,<3.0.0",
    "pydantic-settings>=2.1.0,<3.0.0",
]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

### 2. Create Base Models and Types (45 minutes)
**File: `src/kaltura_mcp/models/base.py`**
```python
"""Base Pydantic models and types for Kaltura MCP."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
import json


class KalturaMediaType(str, Enum):
    """Kaltura media types."""
    VIDEO = "1"
    IMAGE = "2"
    AUDIO = "5"
    LIVE_STREAM = "201"
    LIVE_CHANNEL = "202"


class KalturaEntryStatus(str, Enum):
    """Kaltura entry status values."""
    ERROR_IMPORTING = "-2"
    ERROR_CONVERTING = "-1"
    IMPORT = "0"
    PRECONVERT = "1"
    READY = "2"
    DELETED = "3"
    PENDING = "4"
    MODERATE = "5"
    BLOCKED = "6"
    NO_CONTENT = "7"


class KalturaAssetStatus(str, Enum):
    """Kaltura asset status values."""
    ERROR = "-1"
    QUEUED = "0"
    READY = "2"
    DELETED = "3"
    IMPORTING = "7"
    VALIDATING = "4"


class ResponseStatus(str, Enum):
    """Response status indicators."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


class BaseRequest(BaseModel):
    """Base class for all tool requests."""
    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True
    )


class BaseResponse(BaseModel):
    """Base class for all tool responses."""
    model_config = ConfigDict(
        extra='allow',
        use_enum_values=True,
        populate_by_name=True
    )
    
    status: ResponseStatus = Field(default=ResponseStatus.SUCCESS)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True, indent=2)


class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    message: str
    error_type: str
    input_value: Optional[Any] = None


class ErrorResponse(BaseResponse):
    """Standard error response."""
    status: ResponseStatus = Field(default=ResponseStatus.ERROR)
    error: str
    error_type: str = Field(default="APIError")
    operation: str
    context: Optional[Dict[str, Any]] = None
    details: Optional[List[ErrorDetail]] = None
    suggestion: Optional[str] = None
    traceback: Optional[str] = None


class ValidationErrorResponse(ErrorResponse):
    """Validation error response."""
    error_type: str = Field(default="ValidationError")
    details: List[ErrorDetail]
    
    @classmethod
    def from_pydantic_error(cls, error: Exception, operation: str) -> 'ValidationErrorResponse':
        """Create from Pydantic validation error."""
        from pydantic import ValidationError
        
        if isinstance(error, ValidationError):
            details = []
            for err in error.errors():
                details.append(ErrorDetail(
                    field='.'.join(str(loc) for loc in err['loc']) if err['loc'] else None,
                    message=err['msg'],
                    error_type=err['type'],
                    input_value=err.get('input')
                ))
            
            return cls(
                error=f"Validation failed for {operation}",
                operation=operation,
                details=details
            )
        
        return cls(
            error=str(error),
            operation=operation,
            details=[ErrorDetail(message=str(error), error_type=type(error).__name__)]
        )


class PaginationInfo(BaseModel):
    """Pagination information."""
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=100, description="Number of items per page")
    total_count: int = Field(ge=0, description="Total number of items")
    offset: int = Field(ge=0, description="Number of items skipped")
    has_more: bool = Field(description="Whether there are more items")
    
    @computed_field
    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        if self.page_size == 0:
            return 0
        return (self.total_count + self.page_size - 1) // self.page_size


class DateRange(BaseModel):
    """Date range validation."""
    after: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="Start date (YYYY-MM-DD)")
    before: Optional[str] = Field(None, pattern=r'^\d{4}-\d{2}-\d{2}$', description="End date (YYYY-MM-DD)")
    
    @field_validator('before')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure before date is after after date."""
        if v and info.data.get('after'):
            from datetime import datetime
            try:
                after_dt = datetime.strptime(info.data['after'], '%Y-%m-%d')
                before_dt = datetime.strptime(v, '%Y-%m-%d')
                if before_dt < after_dt:
                    raise ValueError('before date must be after or equal to after date')
            except ValueError as e:
                if 'before date must be after' in str(e):
                    raise
                raise ValueError('Invalid date format')
        return v


class KalturaEntryId(str):
    """Validated Kaltura entry ID."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        """Validate entry ID format."""
        if not isinstance(v, str):
            raise ValueError('Entry ID must be a string')
        
        if not v:
            raise ValueError('Entry ID cannot be empty')
        
        # Security checks
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Entry ID contains invalid path characters')
        
        dangerous_chars = ['$', '`', ';', '&', '|', '<', '>', '"', "'"]
        if any(char in v for char in dangerous_chars):
            raise ValueError('Entry ID contains dangerous characters')
        
        # Format validation
        import re
        if not re.match(r'^[0-9]+_[a-zA-Z0-9]+$', v):
            raise ValueError('Entry ID must follow format: number_alphanumeric')
        
        # Length validation
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Entry ID must be between 3 and 50 characters')
        
        return v


class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class Dimensions(BaseModel):
    """Image/video dimensions."""
    width: int = Field(ge=1, le=4096, description="Width in pixels")
    height: int = Field(ge=1, le=4096, description="Height in pixels")
    
    @field_validator('width', 'height')
    @classmethod
    def validate_dimension(cls, v):
        """Validate dimension values."""
        if not isinstance(v, int):
            raise ValueError('Dimension must be an integer')
        if v < 1 or v > 4096:
            raise ValueError('Dimension must be between 1 and 4096 pixels')
        return v
```

### 3. Create Media Tool Models (60 minutes)
**File: `src/kaltura_mcp/models/media.py`**
```python
"""Pydantic models for media tools."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, computed_field

from .base import (
    BaseRequest, BaseResponse, KalturaEntryId, KalturaMediaType, 
    KalturaEntryStatus, Dimensions, PaginationInfo
)


# ============================================================================
# Request Models
# ============================================================================

class GetMediaEntryRequest(BaseRequest):
    """Request for getting media entry details."""
    entry_id: KalturaEntryId = Field(description="The Kaltura entry ID to retrieve")


class GetDownloadUrlRequest(BaseRequest):
    """Request for getting download URL."""
    entry_id: KalturaEntryId = Field(description="Media entry ID")
    flavor_id: Optional[str] = Field(
        None, 
        pattern=r"^[0-9]+_[a-zA-Z0-9]+$",
        description="Optional specific flavor ID"
    )


class GetThumbnailUrlRequest(BaseRequest):
    """Request for getting thumbnail URL."""
    entry_id: KalturaEntryId = Field(description="Media entry ID")
    width: int = Field(default=120, ge=1, le=4096, description="Thumbnail width in pixels")
    height: int = Field(default=90, ge=1, le=4096, description="Thumbnail height in pixels")
    second: int = Field(default=5, ge=0, description="Video second to capture (for videos)")
    quality: int = Field(default=75, ge=1, le=100, description="JPEG quality (1-100)")


class ListMediaEntriesRequest(BaseRequest):
    """Request for listing media entries."""
    search_text: Optional[str] = Field(None, max_length=500, description="Optional search text")
    media_type: Optional[KalturaMediaType] = Field(None, description="Optional media type filter")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of entries")
    offset: int = Field(default=0, ge=0, description="Number of entries to skip")


# ============================================================================
# Response Models
# ============================================================================

class MediaEntryInfo(BaseModel):
    """Media entry information."""
    id: str
    name: str
    description: Optional[str] = None
    media_type: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    tags: Optional[str] = None
    categories: Optional[str] = None
    categories_ids: Optional[str] = None
    thumbnail_url: Optional[str] = None
    download_url: Optional[str] = None
    plays: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    last_played_at: Optional[datetime] = None
    width: Optional[int] = Field(None, ge=0)
    height: Optional[int] = Field(None, ge=0)
    data_url: Optional[str] = None
    flavor_params_ids: Optional[str] = None
    
    @computed_field
    @property
    def duration_formatted(self) -> Optional[str]:
        """Human-readable duration."""
        if not self.duration:
            return None
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @computed_field
    @property
    def aspect_ratio(self) -> Optional[float]:
        """Calculate aspect ratio."""
        if self.width and self.height and self.height > 0:
            return round(self.width / self.height, 2)
        return None


class GetMediaEntryResponse(BaseResponse):
    """Response for getting media entry details."""
    entry: MediaEntryInfo


class FlavorInfo(BaseModel):
    """Flavor asset information."""
    id: str
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    bitrate: Optional[int] = Field(None, ge=0, description="Bitrate in kbps")
    format: Optional[str] = None
    is_original: bool = False
    container_format: Optional[str] = None
    video_codec: Optional[str] = None
    width: Optional[int] = Field(None, ge=0)
    height: Optional[int] = Field(None, ge=0)
    
    @computed_field
    @property
    def file_size_formatted(self) -> Optional[str]:
        """Human-readable file size."""
        if not self.file_size:
            return None
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} PB"


class GetDownloadUrlResponse(BaseResponse):
    """Response for getting download URL."""
    entry_id: str
    entry_name: str
    flavor: FlavorInfo
    download_url: str


class ThumbnailParameters(BaseModel):
    """Thumbnail generation parameters."""
    width: int
    height: int
    quality: int
    second: Optional[int] = None


class GetThumbnailUrlResponse(BaseResponse):
    """Response for getting thumbnail URL."""
    entry_id: str
    entry_name: str
    media_type: str
    thumbnail_url: str
    original_thumbnail_url: str
    parameters: ThumbnailParameters


class MediaEntryListItem(BaseModel):
    """Simplified media entry for list responses."""
    id: str
    name: str
    description: Optional[str] = None
    media_type: str
    status: str
    created_at: Optional[datetime] = None
    duration: Optional[int] = None
    tags: Optional[str] = None
    thumbnail_url: Optional[str] = None
    plays: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)


class MediaFilters(BaseModel):
    """Applied filters for media listing."""
    search_text: Optional[str] = None
    media_type: Optional[str] = None


class ListMediaEntriesResponse(BaseResponse):
    """Response for listing media entries."""
    entries: List[MediaEntryListItem]
    pagination: PaginationInfo
    filters: MediaFilters
    
    @computed_field
    @property
    def total_duration(self) -> int:
        """Total duration of all entries in seconds."""
        return sum(entry.duration or 0 for entry in self.entries)
    
    @computed_field
    @property
    def total_plays(self) -> int:
        """Total plays across all entries."""
        return sum(entry.plays for entry in self.entries)
    
    @computed_field
    @property
    def total_views(self) -> int:
        """Total views across all entries."""
        return sum(entry.views for entry in self.entries)


# ============================================================================
# Validation Mixins
# ============================================================================

class MediaValidationMixin:
    """Mixin for media-related validation."""
    
    @field_validator('entry_id')
    @classmethod
    def validate_entry_id_format(cls, v):
        """Additional validation for entry ID."""
        if isinstance(v, str):
            return KalturaEntryId.validate(v)
        return v
    
    @field_validator('flavor_id')
    @classmethod
    def validate_flavor_id_format(cls, v):
        """Validate flavor ID format."""
        if v is None:
            return v
        
        if not isinstance(v, str):
            raise ValueError('Flavor ID must be a string')
        
        import re
        if not re.match(r'^[0-9]+_[a-zA-Z0-9]+$', v):
            raise ValueError('Flavor ID must follow format: number_alphanumeric')
        
        return v


# Apply validation mixin to request classes
class ValidatedGetDownloadUrlRequest(GetDownloadUrlRequest, MediaValidationMixin):
    """Download URL request with validation."""
    pass


class ValidatedGetThumbnailUrlRequest(GetThumbnailUrlRequest, MediaValidationMixin):
    """Thumbnail URL request with validation."""
    pass
```

### 4. Create Search Tool Models (75 minutes)
**File: `src/kaltura_mcp/models/search.py`**
```python
"""Pydantic models for search tools."""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, computed_field

from .base import (
    BaseRequest, BaseResponse, SortOrder, DateRange, PaginationInfo
)


# ============================================================================
# Enums and Types
# ============================================================================

class SearchType(str, Enum):
    """Types of search operations."""
    UNIFIED = "unified"
    ENTRY = "entry"
    CAPTION = "caption"
    METADATA = "metadata"
    CUEPOINT = "cuepoint"


class MatchType(str, Enum):
    """Types of matching for search."""
    PARTIAL = "partial"
    EXACT_MATCH = "exact_match"
    STARTS_WITH = "starts_with"
    EXISTS = "exists"
    RANGE = "range"


class BooleanOperator(str, Enum):
    """Boolean operators for search."""
    AND = "and"
    OR = "or"
    NOT = "not"


class SearchField(str, Enum):
    """Available search fields."""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    NAME = "name"
    VIEWS = "views"
    PLAYS = "plays"
    RANK = "rank"


class SpecificField(str, Enum):
    """Specific fields for targeted search."""
    NAME = "name"
    DESCRIPTION = "description"
    TAGS = "tags"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    USER_ID = "user_id"


# ============================================================================
# Request Models
# ============================================================================

class CustomMetadata(BaseModel):
    """Custom metadata search parameters."""
    profile_id: Optional[int] = Field(None, ge=1, description="Metadata profile ID")
    xpath: Optional[str] = Field(None, max_length=500, description="XPath expression")


class SearchEntriesRequest(BaseRequest):
    """Request for searching media entries."""
    query: str = Field(
        min_length=1, 
        max_length=500, 
        description="Search query. Use '*' to list all entries, keywords for specific content"
    )
    search_type: SearchType = Field(
        default=SearchType.UNIFIED,
        description="Type of search to perform"
    )
    match_type: MatchType = Field(
        default=MatchType.PARTIAL,
        description="How to match the search query"
    )
    specific_field: Optional[SpecificField] = Field(
        None,
        description="Search in a specific field"
    )
    boolean_operator: BooleanOperator = Field(
        default=BooleanOperator.AND,
        description="Boolean operator for multiple terms"
    )
    include_highlights: bool = Field(
        default=True,
        description="Include search result highlights"
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
    sort_field: SearchField = Field(
        default=SearchField.CREATED_AT,
        description="Field to sort by"
    )
    sort_order: SortOrder = Field(
        default=SortOrder.DESC,
        description="Sort order"
    )
    date_range: Optional[DateRange] = Field(
        None,
        description="Date range filter"
    )
    custom_metadata: Optional[CustomMetadata] = Field(
        None,
        description="Custom metadata search parameters"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate search query."""
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        
        # Security validation
        dangerous_patterns = ['<script', 'javascript:', 'data:', 'vbscript:']
        query_lower = v.lower()
        if any(pattern in query_lower for pattern in dangerous_patterns):
            raise ValueError('Query contains potentially dangerous content')
        
        return v.strip()


class ListCategoriesRequest(BaseRequest):
    """Request for listing categories."""
    search_text: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional search text to filter categories"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of categories to return"
    )


# ============================================================================
# Response Models
# ============================================================================

class SearchHighlight(BaseModel):
    """Search result highlight."""
    field_name: str
    hits: List[str] = Field(default_factory=list)


class SearchEntryResult(BaseModel):
    """Individual search result entry."""
    id: str
    name: str
    description: Optional[str] = None
    media_type: str
    created_at: Optional[datetime] = None
    duration: Optional[int] = Field(None, ge=0)
    tags: Optional[str] = None
    thumbnail_url: Optional[str] = None
    plays: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    highlights: Optional[List[SearchHighlight]] = None
    
    @computed_field
    @property
    def relevance_score(self) -> float:
        """Calculate relevance score based on available data."""
        # Simple scoring algorithm
        score = 0.0
        
        # Base score for having content
        if self.name:
            score += 10.0
        if self.description:
            score += 5.0
        if self.tags:
            score += 3.0
        
        # Popularity score
        if self.plays > 0:
            score += min(self.plays / 100, 20.0)
        if self.views > 0:
            score += min(self.views / 200, 15.0)
        
        # Highlight bonus
        if self.highlights:
            score += len(self.highlights) * 2.0
        
        return round(score, 2)


class SearchConfiguration(BaseModel):
    """Search configuration used."""
    scope: str
    match_type: str
    specific_field: Optional[str] = None
    boolean_operator: str
    highlights_enabled: bool
    sort_field: str
    sort_order: str


class SearchCapabilities(BaseModel):
    """Available search capabilities."""
    available_scopes: List[str] = Field(
        default=[
            "unified (all content)",
            "entry (metadata)",
            "caption (transcripts)",
            "metadata (custom fields)",
            "cuepoint (temporal markers)"
        ]
    )
    available_match_types: List[str] = Field(
        default=[
            "partial (contains)",
            "exact_match (exact phrase)",
            "starts_with (prefix)",
            "exists (field has value)",
            "range (numeric/date)"
        ]
    )
    advanced_features: List[str] = Field(
        default=[
            "highlighting",
            "boolean operators",
            "custom metadata search",
            "date filtering",
            "field-specific search"
        ]
    )


class SearchContext(BaseModel):
    """Context information about the search."""
    search_query: str
    operation_type: str
    search_configuration: SearchConfiguration
    filters: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    search_capabilities: SearchCapabilities = Field(default_factory=SearchCapabilities)


class SearchEntriesResponse(BaseResponse):
    """Response for searching entries."""
    entries: List[SearchEntryResult]
    total_count: int = Field(ge=0)
    search_context: SearchContext
    
    @computed_field
    @property
    def average_relevance(self) -> float:
        """Average relevance score of results."""
        if not self.entries:
            return 0.0
        
        total_score = sum(entry.relevance_score for entry in self.entries)
        return round(total_score / len(self.entries), 2)
    
    @computed_field
    @property
    def has_highlights(self) -> bool:
        """Whether any results have highlights."""
        return any(entry.highlights for entry in self.entries)


class CategoryInfo(BaseModel):
    """Category information."""
    id: int
    name: str
    description: Optional[str] = None
    tags: Optional[str] = None
    full_name: str
    depth: int = Field(ge=0)
    entries_count: int = Field(default=0, ge=0)
    created_at: Optional[datetime] = None
    parent_id: Optional[int] = None
    partner_id: int


class ListCategoriesResponse(BaseResponse):
    """Response for listing categories."""
    categories: List[CategoryInfo]
    total_count: int = Field(ge=0)
    search_text: Optional[str] = None
    limit: int
    
    @computed_field
    @property
    def total_entries(self) -> int:
        """Total entries across all categories."""
        return sum(cat.entries_count for cat in self.categories)
    
    @computed_field
    @property
    def max_depth(self) -> int:
        """Maximum category depth."""
        if not self.categories:
            return 0
        return max(cat.depth for cat in self.categories)


# ============================================================================
# Validation Helpers
# ============================================================================

class SearchValidationMixin:
    """Mixin for search-related validation."""
    
    @field_validator('search_text')
    @classmethod
    def validate_search_text(cls, v):
        """Validate search text."""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        # Security validation
        dangerous_patterns = ['<script', 'javascript:', 'data:']
        v_lower = v.lower()
        if any(pattern in v_lower for pattern in dangerous_patterns):
            raise ValueError('Search text contains potentially dangerous content')
        
        return v


# Apply validation mixin
class ValidatedListCategoriesRequest(ListCategoriesRequest, SearchValidationMixin):
    """Categories request with validation."""
    pass
```

### 5. Create Analytics Tool Models (60 minutes)
**File: `src/kaltura_mcp/models/analytics.py`**
```python
"""Pydantic models for analytics tools."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, computed_field

from .base import (
    BaseRequest, BaseResponse, KalturaEntryId, DateRange
)


# ============================================================================
# Enums and Types
# ============================================================================

class ReportType(str, Enum):
    """Available report types."""
    CONTENT = "content"
    USER_ENGAGEMENT = "user_engagement"
    CONTRIBUTORS = "contributors"
    GEOGRAPHIC = "geographic"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"
    SYSTEM = "system"
    PLATFORMS = "platforms"
    OPERATING_SYSTEM = "operating_system"
    BROWSERS = "browsers"


class MetricType(str, Enum):
    """Available metric types."""
    PLAYS = "plays"
    VIEWS = "views"
    ENGAGEMENT = "engagement"
    DROP_OFF = "drop_off"
    BANDWIDTH = "bandwidth"
    STORAGE = "storage"


# ============================================================================
# Request Models
# ============================================================================

class GetAnalyticsRequest(BaseRequest):
    """Request for analytics data."""
    from_date: str = Field(
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="Start date for analytics (YYYY-MM-DD format)"
    )
    to_date: str = Field(
        pattern=r'^\d{4}-\d{2}-\d{2}$',
        description="End date for analytics (YYYY-MM-DD format)"
    )
    entry_id: Optional[KalturaEntryId] = Field(
        None,
        description="Optional specific entry ID for entry-specific analytics"
    )
    report_type: ReportType = Field(
        default=ReportType.CONTENT,
        description="Type of analytics report"
    )
    categories: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional category filter (use full category name including parent paths)"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )
    metrics: Optional[List[MetricType]] = Field(
        None,
        description="Metrics to retrieve (for reference/interpretation)"
    )
    
    @field_validator('from_date', 'to_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date format and value."""
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @field_validator('to_date')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure to_date is after from_date."""
        if 'from_date' in info.data:
            try:
                from_dt = date.fromisoformat(info.data['from_date'])
                to_dt = date.fromisoformat(v)
                
                if to_dt < from_dt:
                    raise ValueError('to_date must be after or equal to from_date')
                
                # Validate range is not too large (max 1 year)
                if (to_dt - from_dt).days > 365:
                    raise ValueError('Date range cannot exceed 365 days')
                    
            except ValueError as e:
                if 'must be after' in str(e) or 'cannot exceed' in str(e):
                    raise
                raise ValueError('Invalid date format')
        
        return v


# ============================================================================
# Response Models
# ============================================================================

class AnalyticsDataPoint(BaseModel):
    """Individual analytics data point."""
    name: Optional[str] = None
    value: Union[int, float, str]
    label: Optional[str] = None
    percentage: Optional[float] = Field(None, ge=0, le=100)
    rank: Optional[int] = Field(None, ge=1)
    
    @computed_field
    @property
    def formatted_value(self) -> str:
        """Format value for display."""
        if isinstance(self.value, (int, float)):
            if self.value >= 1000000:
                return f"{self.value/1000000:.1f}M"
            elif self.value >= 1000:
                return f"{self.value/1000:.1f}K"
            else:
                return str(int(self.value))
        return str(self.value)


class SummaryStatistics(BaseModel):
    """Summary statistics for analytics data."""
    total: Union[int, float] = 0
    average: Union[int, float] = 0
    maximum: Union[int, float] = 0
    minimum: Union[int, float] = 0
    median: Optional[Union[int, float]] = None
    count: int = 0
    
    @computed_field
    @property
    def range_value(self) -> Union[int, float]:
        """Calculate range (max - min)."""
        return self.maximum - self.minimum


class ReportMetadata(BaseModel):
    """Metadata about the analytics report."""
    report_type: str
    report_type_code: str
    date_range: Dict[str, str]
    entry_id: Optional[str] = None
    categories: Optional[str] = None
    requested_metrics: List[str]
    headers: List[str] = Field(default_factory=list)
    total_results: int = 0
    
    @computed_field
    @property
    def date_range_days(self) -> int:
        """Calculate number of days in date range."""
        try:
            from_date = date.fromisoformat(self.date_range['from'])
            to_date = date.fromisoformat(self.date_range['to'])
            return (to_date - from_date).days + 1
        except (ValueError, KeyError):
            return 0


class GetAnalyticsResponse(BaseResponse):
    """Response for analytics data."""
    metadata: ReportMetadata
    data: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[Dict[str, SummaryStatistics]] = None
    
    @computed_field
    @property
    def has_data(self) -> bool:
        """Whether the response contains data."""
        return len(self.data) > 0
    
    @computed_field
    @property
    def data_points_count(self) -> int:
        """Number of data points."""
        return len(self.data)
    
    def get_column_values(self, column: str) -> List[Union[int, float]]:
        """Get numeric values for a specific column."""
        values = []
        for row in self.data:
            if column in row:
                value = row[column]
                if isinstance(value, (int, float)):
                    values.append(value)
        return values
    
    def calculate_summary_for_column(self, column: str) -> Optional[SummaryStatistics]:
        """Calculate summary statistics for a column."""
        values = self.get_column_values(column)
        if not values:
            return None
        
        return SummaryStatistics(
            total=sum(values),
            average=sum(values) / len(values),
            maximum=max(values),
            minimum=min(values),
            count=len(values)
        )


# ============================================================================
# Error Models
# ============================================================================

class AnalyticsUnavailableResponse(BaseResponse):
    """Response when analytics are not available."""
    error: str = "Analytics functionality is not available"
    detail: str
    suggestion: str = "Ensure the Kaltura Python client includes the Report plugin"
    from_date: str
    to_date: str
    entry_id: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.status = "error"


# ============================================================================
# Validation Helpers
# ============================================================================

class AnalyticsValidationMixin:
    """Mixin for analytics-related validation."""
    
    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        """Validate categories filter."""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        # Basic security validation
        if any(char in v for char in ['<', '>', '"', "'"]):
            raise ValueError('Categories filter contains invalid characters')
        
        return v
    
    @field_validator('metrics')
    @classmethod
    def validate_metrics(cls, v):
        """Validate metrics list."""
        if v is None:
            return v
        
        if not isinstance(v, list):
            raise ValueError('Metrics must be a list')
        
        if len(v) > 10:
            raise ValueError('Maximum 10 metrics allowed')
        
        return v


# Apply validation mixin
class ValidatedGetAnalyticsRequest(GetAnalyticsRequest, AnalyticsValidationMixin):
    """Analytics request with validation."""
    pass
```

### 6. Create Assets Tool Models (60 minutes)
**File: `src/kaltura_mcp/models/assets.py`**
```python
"""Pydantic models for asset tools."""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, computed_field

from .base import (
    BaseRequest, BaseResponse, KalturaEntryId, KalturaAssetStatus
)


# ============================================================================
# Enums and Types
# ============================================================================

class CaptionFormat(str, Enum):
    """Caption format types."""
    SRT = "srt"
    VTT = "vtt"
    DFXP = "dfxp"
    CAP = "cap"
    SCC = "scc"


class AttachmentFormat(str, Enum):
    """Attachment format types."""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    TXT = "txt"
    XML = "xml"
    JSON = "json"


class DownloadStatus(str, Enum):
    """Download status values."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ENCODING_ERROR = "encoding_error"


# ============================================================================
# Request Models
# ============================================================================

class ListCaptionAssetsRequest(BaseRequest):
    """Request for listing caption assets."""
    entry_id: KalturaEntryId = Field(description="Media entry ID")


class GetCaptionContentRequest(BaseRequest):
    """Request for getting caption content."""
    caption_asset_id: str = Field(
        min_length=1,
        max_length=50,
        description="Caption asset ID to retrieve content for"
    )
    download_content: bool = Field(
        default=True,
        description="Whether to download and include the caption text"
    )
    
    @field_validator('caption_asset_id')
    @classmethod
    def validate_caption_asset_id(cls, v):
        """Validate caption asset ID format."""
        if not v or not isinstance(v, str):
            raise ValueError('Caption asset ID is required and must be a string')
        
        v = v.strip()
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Caption asset ID must be between 1 and 50 characters')
        
        # Basic security validation
        dangerous_chars = ['..', '/', '\\', '<', '>', '"', "'"]
        if any(char in v for char in dangerous_chars):
            raise ValueError('Caption asset ID contains invalid characters')
        
        return v


class ListAttachmentAssetsRequest(BaseRequest):
    """Request for listing attachment assets."""
    entry_id: KalturaEntryId = Field(description="Media entry ID")


class GetAttachmentContentRequest(BaseRequest):
    """Request for getting attachment content."""
    attachment_asset_id: str = Field(
        min_length=1,
        max_length=50,
        description="Attachment asset ID to retrieve content for"
    )
    download_content: bool = Field(
        default=False,
        description="Whether to download and include the attachment content"
    )
    max_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum file size to download in MB"
    )
    
    @field_validator('attachment_asset_id')
    @classmethod
    def validate_attachment_asset_id(cls, v):
        """Validate attachment asset ID format."""
        if not v or not isinstance(v, str):
            raise ValueError('Attachment asset ID is required and must be a string')
        
        v = v.strip()
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Attachment asset ID must be between 1 and 50 characters')
        
        # Basic security validation
        dangerous_chars = ['..', '/', '\\', '<', '>', '"', "'"]
        if any(char in v for char in dangerous_chars):
            raise ValueError('Attachment asset ID contains invalid characters')
        
        return v


# ============================================================================
# Response Models
# ============================================================================

class CaptionAssetInfo(BaseModel):
    """Caption asset information."""
    id: str
    entry_id: str
    language: Optional[str] = None
    language_code: Optional[str] = None
    label: Optional[str] = None
    format: Optional[str] = None
    status: Optional[str] = None
    file_ext: Optional[str] = None
    size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    accuracy: Optional[float] = Field(None, ge=0, le=100, description="Accuracy percentage")
    is_default: Optional[bool] = None
    
    @computed_field
    @property
    def size_formatted(self) -> Optional[str]:
        """Human-readable file size."""
        if not self.size:
            return None
        
        for unit in ['B', 'KB', 'MB']:
            if self.size < 1024.0:
                return f"{self.size:.1f} {unit}"
            self.size /= 1024.0
        return f"{self.size:.1f} GB"
    
    @computed_field
    @property
    def accuracy_formatted(self) -> Optional[str]:
        """Formatted accuracy percentage."""
        if self.accuracy is None:
            return None
        return f"{self.accuracy:.1f}%"


class ListCaptionAssetsResponse(BaseResponse):
    """Response for listing caption assets."""
    entry_id: str
    total_count: int = Field(ge=0)
    caption_assets: List[CaptionAssetInfo]
    
    @computed_field
    @property
    def available_languages(self) -> List[str]:
        """List of available languages."""
        languages = set()
        for asset in self.caption_assets:
            if asset.language:
                languages.add(asset.language)
        return sorted(list(languages))
    
    @computed_field
    @property
    def default_caption(self) -> Optional[CaptionAssetInfo]:
        """Get the default caption asset."""
        for asset in self.caption_assets:
            if asset.is_default:
                return asset
        return None


class CaptionContentInfo(BaseModel):
    """Caption content information."""
    caption_asset_id: str
    entry_id: str
    language: str
    label: Optional[str] = None
    format: str
    content_url: str
    size: Optional[int] = None
    accuracy: Optional[float] = None
    filename: str
    download_status: DownloadStatus
    caption_text: Optional[str] = None
    text_length: Optional[int] = None
    encoding: Optional[str] = None
    download_error: Optional[str] = None
    note: str
    
    @computed_field
    @property
    def has_content(self) -> bool:
        """Whether caption text is available."""
        return self.caption_text is not None
    
    @computed_field
    @property
    def word_count(self) -> Optional[int]:
        """Estimate word count."""
        if not self.caption_text:
            return None
        
        # Simple word count (remove timestamp lines and count words)
        import re
        # Remove SRT/VTT timestamp lines
        text = re.sub(r'\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}', '', self.caption_text)
        # Remove sequence numbers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        # Count words
        words = text.split()
        return len([word for word in words if word.strip()])


class GetCaptionContentResponse(BaseResponse):
    """Response for getting caption content."""
    caption: CaptionContentInfo


class AttachmentAssetInfo(BaseModel):
    """Attachment asset information."""
    id: str
    entry_id: str
    filename: str
    title: Optional[str] = None
    format: str
    status: str
    file_ext: Optional[str] = None
    size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    
    @computed_field
    @property
    def size_formatted(self) -> Optional[str]:
        """Human-readable file size."""
        if not self.size:
            return None
        
        size = self.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @computed_field
    @property
    def file_type(self) -> str:
        """Determine file type from extension."""
        if not self.file_ext:
            return "Unknown"
        
        ext = self.file_ext.lower()
        
        if ext in ['pdf']:
            return "PDF Document"
        elif ext in ['doc', 'docx']:
            return "Word Document"
        elif ext in ['txt']:
            return "Text File"
        elif ext in ['xml']:
            return "XML Document"
        elif ext in ['json']:
            return "JSON Data"
        elif ext in ['jpg', 'jpeg', 'png', 'gif']:
            return "Image"
        else:
            return f"{ext.upper()} File"


class ListAttachmentAssetsResponse(BaseResponse):
    """Response for listing attachment assets."""
    entry_id: str
    total_count: int = Field(ge=0)
    attachment_assets: List[AttachmentAssetInfo]
    
    @computed_field
    @property
    def total_size(self) -> int:
        """Total size of all attachments in bytes."""
        return sum(asset.size or 0 for asset in self.attachment_assets)
    
    @computed_field
    @property
    def file_types(self) -> List[str]:
        """List of unique file types."""
        types = set()
        for asset in self.attachment_assets:
            types.add(asset.file_type)
        return sorted(list(types))


class AttachmentContentInfo(BaseModel):
    """Attachment content information."""
    attachment_asset_id: str
    entry_id: str
    filename: str
    title: Optional[str] = None
    format: str
    download_url: str
    size: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    download_status: DownloadStatus
    content: Optional[str] = None
    content_encoding: Optional[Literal["base64"]] = None
    actual_size: Optional[int] = None
    download_error: Optional[str] = None
    note: str
    
    @computed_field
    @property
    def has_content(self) -> bool:
        """Whether attachment content is available."""
        return self.content is not None
    
    @computed_field
    @property
    def compression_ratio(self) -> Optional[float]:
        """Calculate compression ratio if content is available."""
        if not self.has_content or not self.actual_size or not self.size:
            return None
        
        return round(self.actual_size / self.size, 2)


class GetAttachmentContentResponse(BaseResponse):
    """Response for getting attachment content."""
    attachment: AttachmentContentInfo


# ============================================================================
# Error Models
# ============================================================================

class AssetUnavailableResponse(BaseResponse):
    """Response when asset functionality is not available."""
    error: str
    asset_type: Literal["caption", "attachment"]
    entry_id: Optional[str] = None
    asset_id: Optional[str] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        self.status = "error"


# ============================================================================
# Validation Helpers
# ============================================================================

class AssetValidationMixin:
    """Mixin for asset-related validation."""
    
    @field_validator('entry_id')
    @classmethod
    def validate_entry_id_format(cls, v):
        """Validate entry ID format."""
        if isinstance(v, str):
            return KalturaEntryId.validate(v)
        return v
```

### 7. Update Tool Registry with Pydantic Integration (90 minutes)
**File: `src/kaltura_mcp/tool_registry.py`** (Enhanced with Pydantic)
```python
"""Enhanced tool registry with Pydantic integration."""

import logging
from typing import Dict, List, Type, Optional, Any, Set, Union
from collections import defaultdict
import importlib
import pkgutil

import mcp.types as types
from pydantic import BaseModel, ValidationError

from .tools.base import BaseTool, ToolExecutionError
from .kaltura_client import KalturaClientManager
from .models.base import BaseRequest, BaseResponse, ValidationErrorResponse

logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    """Exception raised by tool registry operations."""
    pass


class EnhancedToolRegistry:
    """Enhanced registry with Pydantic validation support."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._tool_classes: Dict[str, Type[BaseTool]] = {}
        self._request_models: Dict[str, Type[BaseRequest]] = {}
        self._response_models: Dict[str, Type[BaseResponse]] = {}
        self._categories: Dict[str, Set[str]] = defaultdict(set)
        self._initialized = False
        
        logger.info("Enhanced tool registry initialized")
    
    def register(self, tool_class: Type[BaseTool], 
                 request_model: Optional[Type[BaseRequest]] = None,
                 response_model: Optional[Type[BaseResponse]] = None,
                 category: Optional[str] = None) -> None:
        """
        Register a tool class with optional Pydantic models.
        
        Args:
            tool_class: The tool class to register
            request_model: Pydantic model for request validation
            response_model: Pydantic model for response formatting
            category: Optional category for organization
        """
        # Create tool instance to get name
        try:
            tool_instance = tool_class()
        except Exception as e:
            raise ToolRegistryError(f"Failed to instantiate tool {tool_class.__name__}: {e}")
        
        tool_name = tool_instance.name
        
        # Check for duplicate registration
        if tool_name in self._tools:
            existing_class = self._tool_classes[tool_name]
            if existing_class != tool_class:
                raise ToolRegistryError(
                    f"Tool '{tool_name}' already registered with different class "
                    f"(existing: {existing_class.__name__}, new: {tool_class.__name__})"
                )
            logger.debug(f"Tool '{tool_name}' already registered, skipping")
            return
        
        # Validate tool
        self._validate_tool(tool_instance)
        
        # Register tool and models
        self._tools[tool_name] = tool_instance
        self._tool_classes[tool_name] = tool_class
        
        if request_model:
            self._request_models[tool_name] = request_model
        
        if response_model:
            self._response_models[tool_name] = response_model
        
        # Add to category
        if category:
            self._categories[category].add(tool_name)
        
        logger.info(f"Registered tool: {tool_name} ({tool_class.__name__})")
        if request_model:
            logger.debug(f"  Request model: {request_model.__name__}")
        if response_model:
            logger.debug(f"  Response model: {response_model.__name__}")
    
    def validate_request(self, tool_name: str, **kwargs) -> Union[Dict[str, Any], BaseRequest]:
        """
        Validate request parameters using Pydantic model if available.
        
        Args:
            tool_name: Name of the tool
            **kwargs: Request parameters
            
        Returns:
            Validated parameters as dict or Pydantic model instance
            
        Raises:
            ValidationError: If validation fails
        """
        if tool_name not in self._request_models:
            # No specific model, return as-is
            return kwargs
        
        request_model = self._request_models[tool_name]
        
        try:
            # Create and validate model instance
            validated_request = request_model(**kwargs)
            
            # Return as dict for compatibility, but could return model instance
            return validated_request.model_dump(exclude_none=True)
            
        except ValidationError as e:
            logger.error(f"Request validation failed for {tool_name}: {e}")
            raise
    
    def format_response(self, tool_name: str, data: Any) -> str:
        """
        Format response using Pydantic model if available.
        
        Args:
            tool_name: Name of the tool
            data: Response data
            
        Returns:
            JSON formatted response
        """
        if tool_name not in self._response_models:
            # No specific model, use default formatting
            if isinstance(data, str):
                return data
            
            import json
            return json.dumps(data, indent=2, default=str)
        
        response_model = self._response_models[tool_name]
        
        try:
            if isinstance(data, dict):
                # Create model instance from dict
                response_instance = response_model(**data)
            elif isinstance(data, BaseResponse):
                # Already a response model
                response_instance = data
            else:
                # Wrap in model
                response_instance = response_model(data=data)
            
            return response_instance.to_json()
            
        except Exception as e:
            logger.warning(f"Failed to format response with model for {tool_name}: {e}")
            # Fallback to default formatting
            import json
            return json.dumps(data, indent=2, default=str)
    
    async def execute(self, name: str, manager: KalturaClientManager, **kwargs) -> str:
        """
        Execute a tool with Pydantic validation.
        
        Args:
            name: Tool name to execute
            manager: Kaltura client manager
            **kwargs: Tool arguments
            
        Returns:
            JSON string response
        """
        tool = self.get_tool(name)
        if not tool:
            available_tools = ', '.join(self.list_tool_names())
            error_response = ValidationErrorResponse(
                error=f"Unknown tool: {name}",
                operation="tool_execution",
                context={"available_tools": available_tools}
            )
            return error_response.to_json()
        
        logger.info(f"Executing tool: {name}")
        logger.debug(f"Tool arguments: {kwargs}")
        
        try:
            # Validate request parameters
            validated_kwargs = self.validate_request(name, **kwargs)
            
            # Execute tool
            result = await tool.execute(manager, **validated_kwargs)
            
            # Format response if it's not already formatted
            if not isinstance(result, str):
                result = self.format_response(name, result)
            
            logger.info(f"Tool execution completed: {name}")
            return result
            
        except ValidationError as e:
            logger.error(f"Validation error in tool {name}: {e}")
            error_response = ValidationErrorResponse.from_pydantic_error(e, f"execute {name}")
            return error_response.to_json()
            
        except ToolExecutionError as e:
            logger.error(f"Tool execution error in {name}: {e}")
            error_response = ValidationErrorResponse(
                error=str(e),
                error_type=e.error_type,
                operation=f"execute {name}",
                context=e.context
            )
            return error_response.to_json()
            
        except Exception as e:
            logger.error(f"Unexpected error in tool {name}: {e}", exc_info=True)
            error_response = ValidationErrorResponse(
                error=f"Unexpected error in tool execution: {str(e)}",
                error_type=type(e).__name__,
                operation=f"execute {name}",
                context={"tool": name, "arguments": kwargs}
            )
            return error_response.to_json()
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get JSON schema for tool including request/response models."""
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        
        schema = {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema
        }
        
        # Add request model schema if available
        if tool_name in self._request_models:
            request_model = self._request_models[tool_name]
            schema["request_model_schema"] = request_model.model_json_schema()
        
        # Add response model schema if available
        if tool_name in self._response_models:
            response_model = self._response_models[tool_name]
            schema["response_model_schema"] = response_model.model_json_schema()
        
        return schema
    
    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools."""
        schemas = {}
        for tool_name in self.list_tool_names():
            schemas[tool_name] = self.get_tool_schema(tool_name)
        return schemas
    
    # ... (rest of the methods remain the same as in the previous implementation)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a registered tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[types.Tool]:
        """Get all registered tools as MCP Tool definitions."""
        return [tool.to_mcp_tool() for tool in self._tools.values()]
    
    def list_tool_names(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())
    
    def get_tools_by_category(self, category: str) -> List[str]:
        """Get tool names in a specific category."""
        return list(self._categories.get(category, set()))
    
    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self._categories.keys())
    
    def _validate_tool(self, tool: BaseTool) -> None:
        """Validate tool implementation."""
        errors = []
        
        # Check required attributes
        if not tool.name:
            errors.append("Tool name cannot be empty")
        
        if not tool.description:
            errors.append("Tool description cannot be empty")
        
        if not isinstance(tool.input_schema, dict):
            errors.append("Tool input_schema must be a dictionary")
        
        # Validate schema structure
        schema = tool.input_schema
        if 'type' not in schema:
            errors.append("Tool input_schema must have 'type' field")
        
        if schema.get('type') != 'object':
            errors.append("Tool input_schema type must be 'object'")
        
        if 'properties' not in schema:
            errors.append("Tool input_schema must have 'properties' field")
        
        if errors:
            raise ToolRegistryError(f"Tool validation failed: {'; '.join(errors)}")


# Global enhanced registry instance
enhanced_registry = EnhancedToolRegistry()


def register_tool_with_models(
    request_model: Optional[Type[BaseRequest]] = None,
    response_model: Optional[Type[BaseResponse]] = None,
    category: Optional[str] = None
):
    """
    Enhanced decorator for registering tool classes with Pydantic models.
    
    Args:
        request_model: Pydantic model for request validation
        response_model: Pydantic model for response formatting
        category: Optional category for the tool
    """
    def decorator(cls: Type[BaseTool]) -> Type[BaseTool]:
        enhanced_registry.register(cls, request_model, response_model, category)
        return cls
    
    return decorator


def get_enhanced_registry() -> EnhancedToolRegistry:
    """Get the global enhanced tool registry instance."""
    return enhanced_registry
```

### 8. Update Tool Implementations with Pydantic Models (90 minutes)
**File: `src/kaltura_mcp/tools/media.py`** (Updated with Pydantic)
```python
"""Media tools with Pydantic integration."""

from typing import Dict, Any, Optional

from .base import MediaTool
from .utils import safe_serialize_kaltura_field, format_timestamp
from ..tool_registry import register_tool_with_models
from ..models.media import (
    GetMediaEntryRequest, GetMediaEntryResponse, MediaEntryInfo,
    GetDownloadUrlRequest, GetDownloadUrlResponse, FlavorInfo,
    GetThumbnailUrlRequest, GetThumbnailUrlResponse, ThumbnailParameters,
    ListMediaEntriesRequest, ListMediaEntriesResponse, MediaEntryListItem,
    MediaFilters, PaginationInfo
)


@register_tool_with_models(
    request_model=GetMediaEntryRequest,
    response_model=GetMediaEntryResponse,
    category="media"
)
class GetMediaEntryTool(MediaTool):
    """Tool for retrieving detailed media entry information with Pydantic validation."""
    
    @property
    def name(self) -> str:
        return "get_media_entry"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific media entry"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return GetMediaEntryRequest.model_json_schema()
    
    async def execute(self, manager, **kwargs) -> GetMediaEntryResponse:
        """Execute the get media entry tool with Pydantic validation."""
        # Validate request
        request = GetMediaEntryRequest(**kwargs)
        
        try:
            # Get Kaltura client
            client = manager.get_client()
            
            # Retrieve entry
            entry = client.media.get(request.entry_id)
            
            # Build response using Pydantic model
            entry_info = MediaEntryInfo(
                id=entry.id,
                name=entry.name,
                description=entry.description,
                media_type=safe_serialize_kaltura_field(entry.mediaType),
                status=safe_serialize_kaltura_field(entry.status),
                created_at=format_timestamp(entry.createdAt),
                updated_at=format_timestamp(entry.updatedAt),
                duration=entry.duration,
                tags=entry.tags,
                categories=entry.categories,
                categories_ids=entry.categoriesIds,
                thumbnail_url=entry.thumbnailUrl,
                download_url=entry.downloadUrl,
                plays=entry.plays or 0,
                views=entry.views or 0,
                last_played_at=format_timestamp(entry.lastPlayedAt),
                width=entry.width,
                height=entry.height,
                data_url=entry.dataUrl,
                flavor_params_ids=entry.flavorParamsIds,
            )
            
            return GetMediaEntryResponse(entry=entry_info)
            
        except Exception as e:
            # Return error using parent class error handling
            error_json = self.handle_error(e, "get media entry", {"entry_id": request.entry_id})
            # For this example, we'll raise the exception to be handled by registry
            raise e


@register_tool_with_models(
    request_model=GetThumbnailUrlRequest,
    response_model=GetThumbnailUrlResponse,
    category="media"
)
class GetThumbnailUrlTool(MediaTool):
    """Tool for generating custom thumbnail URLs with Pydantic validation."""
    
    @property
    def name(self) -> str:
        return "get_thumbnail_url"
    
    @property
    def description(self) -> str:
        return "Get video thumbnail/preview image URL with custom dimensions"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return GetThumbnailUrlRequest.model_json_schema()
    
    async def execute(self, manager, **kwargs) -> GetThumbnailUrlResponse:
        """Execute the get thumbnail URL tool with Pydantic validation."""
        # Validate request
        request = GetThumbnailUrlRequest(**kwargs)
        
        try:
            # Get Kaltura client
            client = manager.get_client()
            
            # Get entry to verify it exists and get info
            entry = client.media.get(request.entry_id)
            
            if not entry.thumbnailUrl:
                raise ValueError("No thumbnail available for this entry")
            
            # Build thumbnail URL with parameters
            from .utils import build_url_with_params
            params = {
                "width": request.width,
                "height": request.height,
                "quality": request.quality
            }
            
            # Add video-specific parameters
            from KalturaClient.Plugins.Core import KalturaMediaType
            is_video = hasattr(entry, 'mediaType') and entry.mediaType == KalturaMediaType.VIDEO
            
            if is_video and request.second > 0:
                params["vid_sec"] = request.second
            
            # Construct final URL
            thumbnail_url = build_url_with_params(entry.thumbnailUrl, params)
            
            # Build response using Pydantic model
            parameters = ThumbnailParameters(
                width=request.width,
                height=request.height,
                quality=request.quality,
                second=request.second if is_video else None
            )
            
            return GetThumbnailUrlResponse(
                entry_id=request.entry_id,
                entry_name=entry.name,
                media_type=safe_serialize_kaltura_field(entry.mediaType),
                thumbnail_url=thumbnail_url,
                original_thumbnail_url=entry.thumbnailUrl,
                parameters=parameters
            )
            
        except Exception as e:
            raise e  # Let registry handle error formatting


# Continue with other tools...
```

### 9. Update Servers to Use Enhanced Registry (30 minutes)
**File: `src/kaltura_mcp/server.py`** (Updated sections)
```python
"""Local MCP server using enhanced tool registry with Pydantic."""

import json
from .tool_registry import get_enhanced_registry

# Use enhanced registry
registry = get_enhanced_registry()

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool execution with enhanced validation."""
    try:
        # Use enhanced registry with Pydantic validation
        result = await registry.execute(name, kaltura_manager, **arguments)
        return [types.TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        # Error is already formatted by enhanced registry
        error_response = {
            "error": str(e),
            "tool": name
        }
        return [types.TextContent(type="text", text=json.dumps(error_response, indent=2))]
```

### 10. Create Comprehensive Tests (60 minutes)
**File: `tests/unit/test_pydantic_models.py`**
```python
"""Test Pydantic models and validation."""

import pytest
from pydantic import ValidationError
from datetime import datetime

from kaltura_mcp.models.media import (
    GetMediaEntryRequest, GetMediaEntryResponse, MediaEntryInfo
)
from kaltura_mcp.models.search import SearchEntriesRequest, SearchType
from kaltura_mcp.models.analytics import GetAnalyticsRequest, ReportType
from kaltura_mcp.models.base import ValidationErrorResponse


class TestMediaModels:
    """Test media-related Pydantic models."""
    
    def test_get_media_entry_request_valid(self):
        """Test valid media entry request."""
        request = GetMediaEntryRequest(entry_id="123_abc456")
        assert request.entry_id == "123_abc456"
    
    def test_get_media_entry_request_invalid_id(self):
        """Test invalid entry ID format."""
        with pytest.raises(ValidationError) as exc_info:
            GetMediaEntryRequest(entry_id="invalid_id")
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "Entry ID must follow format" in str(errors[0]['msg'])
    
    def test_get_media_entry_request_security(self):
        """Test security validation."""
        with pytest.raises(ValidationError):
            GetMediaEntryRequest(entry_id="123_../etc/passwd")
        
        with pytest.raises(ValidationError):
            GetMediaEntryRequest(entry_id="123_abc$rm")
    
    def test_media_entry_info_computed_fields(self):
        """Test computed fields in MediaEntryInfo."""
        entry = MediaEntryInfo(
            id="123_abc",
            name="Test Video",
            media_type="1",
            status="2",
            duration=3661,  # 1 hour, 1 minute, 1 second
            width=1920,
            height=1080
        )
        
        assert entry.duration_formatted == "01:01:01"
        assert entry.aspect_ratio == 1.78
    
    def test_media_entry_response(self):
        """Test media entry response model."""
        entry_info = MediaEntryInfo(
            id="123_abc",
            name="Test Video",
            media_type="1",
            status="2"
        )
        
        response = GetMediaEntryResponse(entry=entry_info)
        assert response.status == "success"
        assert response.entry.id == "123_abc"
        
        # Test JSON serialization
        json_str = response.to_json()
        assert "123_abc" in json_str
        assert "success" in json_str


class TestSearchModels:
    """Test search-related Pydantic models."""
    
    def test_search_entries_request_valid(self):
        """Test valid search request."""
        request = SearchEntriesRequest(
            query="test video",
            search_type=SearchType.UNIFIED,
            max_results=50
        )
        
        assert request.query == "test video"
        assert request.search_type == SearchType.UNIFIED
        assert request.max_results == 50
    
    def test_search_entries_request_validation(self):
        """Test search request validation."""
        # Test empty query
        with pytest.raises(ValidationError):
            SearchEntriesRequest(query="")
        
        # Test max results validation
        with pytest.raises(ValidationError):
            SearchEntriesRequest(query="test", max_results=200)
        
        # Test dangerous content
        with pytest.raises(ValidationError):
            SearchEntriesRequest(query="<script>alert('xss')</script>")
    
    def test_search_date_range_validation(self):
        """Test date range validation."""
        from kaltura_mcp.models.base import DateRange
        
        # Valid range
        date_range = DateRange(after="2023-01-01", before="2023-12-31")
        assert date_range.after == "2023-01-01"
        
        # Invalid range (before < after)
        with pytest.raises(ValidationError):
            DateRange(after="2023-12-31", before="2023-01-01")


class TestAnalyticsModels:
    """Test analytics-related Pydantic models."""
    
    def test_analytics_request_valid(self):
        """Test valid analytics request."""
        request = GetAnalyticsRequest(
            from_date="2023-01-01",
            to_date="2023-01-31",
            report_type=ReportType.CONTENT
        )
        
        assert request.from_date == "2023-01-01"
        assert request.to_date == "2023-01-31"
        assert request.report_type == ReportType.CONTENT
    
    def test_analytics_date_validation(self):
        """Test analytics date validation."""
        # Invalid date format
        with pytest.raises(ValidationError):
            GetAnalyticsRequest(
                from_date="2023/01/01",
                to_date="2023-01-31"
            )
        
        # Invalid date range
        with pytest.raises(ValidationError):
            GetAnalyticsRequest(
                from_date="2023-01-31",
                to_date="2023-01-01"
            )
        
        # Range too large (> 365 days)
        with pytest.raises(ValidationError):
            GetAnalyticsRequest(
                from_date="2022-01-01",
                to_date="2023-12-31"
            )


class TestErrorModels:
    """Test error response models."""
    
    def test_validation_error_response(self):
        """Test validation error response creation."""
        try:
            GetMediaEntryRequest(entry_id="invalid")
        except ValidationError as e:
            error_response = ValidationErrorResponse.from_pydantic_error(
                e, "get_media_entry"
            )
            
            assert error_response.error_type == "ValidationError"
            assert error_response.operation == "get_media_entry"
            assert len(error_response.details) > 0
            
            # Test JSON serialization
            json_str = error_response.to_json()
            assert "ValidationError" in json_str
    
    def test_error_response_formatting(self):
        """Test error response JSON formatting."""
        error_response = ValidationErrorResponse(
            error="Test error",
            operation="test_operation",
            details=[]
        )
        
        json_str = error_response.to_json()
        data = json.loads(json_str)
        
        assert data["status"] == "error"
        assert data["error"] == "Test error"
        assert data["operation"] == "test_operation"
        assert "timestamp" in data


class TestToolRegistry:
    """Test enhanced tool registry with Pydantic."""
    
    def test_request_validation(self):
        """Test request validation in registry."""
        from kaltura_mcp.tool_registry import get_enhanced_registry
        
        registry = get_enhanced_registry()
        
        # This would require actual tool registration to test properly
        # For now, just test that the method exists
        assert hasattr(registry, 'validate_request')
        assert hasattr(registry, 'format_response')
        assert hasattr(registry, 'get_tool_schema')
```

## Testing the Implementation

### 1. Test Pydantic Integration
```bash
# Test model validation
python -c "
from kaltura_mcp.models.media import GetMediaEntryRequest
try:
    req = GetMediaEntryRequest(entry_id='invalid')
except Exception as e:
    print('Validation works:', e)
"

# Test enhanced registry
python -c "
from kaltura_mcp.tool_registry import get_enhanced_registry
registry = get_enhanced_registry()
print('Enhanced registry available')
"
```

### 2. Run Comprehensive Tests
```bash
pytest tests/unit/test_pydantic_models.py -v
pytest tests/unit/test_tool_registry.py -v  # If exists
pytest tests/ -k "pydantic" -v
```

## Benefits
- ✅ Runtime input validation with detailed error messages
- ✅ Type safety throughout the application
- ✅ Better IDE support with auto-completion
- ✅ Automatic API documentation generation
- ✅ Consistent data serialization/deserialization
- ✅ Security improvements through validation
- ✅ Better error handling with structured feedback
- ✅ Reduced boilerplate code for validation
- ✅ Clear data contracts between components
- ✅ Future-proof for API evolution

## Files Created
- `src/kaltura_mcp/models/__init__.py`
- `src/kaltura_mcp/models/base.py`
- `src/kaltura_mcp/models/media.py`
- `src/kaltura_mcp/models/search.py`
- `src/kaltura_mcp/models/analytics.py`
- `src/kaltura_mcp/models/assets.py`
- `tests/unit/test_pydantic_models.py`

## Files Modified
- `pyproject.toml` (added Pydantic dependencies)
- `src/kaltura_mcp/tool_registry.py` (enhanced with Pydantic)
- `src/kaltura_mcp/tools/media.py` (updated with Pydantic models)
- `src/kaltura_mcp/server.py` (updated to use enhanced registry)

## Next Steps
1. Complete Pydantic integration for all tools
2. Add API documentation generation using Pydantic schemas
3. Implement request/response caching with type safety
4. Add performance monitoring for validation overhead
5. Create OpenAPI specification generation from Pydantic models