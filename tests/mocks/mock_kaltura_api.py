"""
Mock Kaltura API for offline testing.

This module provides a mock implementation of the Kaltura API for testing
without requiring a real Kaltura API connection.
"""
import asyncio
import json
import uuid
import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from unittest.mock import AsyncMock, MagicMock, patch

# Import Kaltura client types for type compatibility
try:
    from KalturaClient.Plugins.Core import (
        KalturaMediaEntry, KalturaMediaEntryFilter, KalturaFilterPager,
        KalturaMediaEntryListResponse, KalturaMediaType, KalturaMediaEntryStatus,
        KalturaCategory, KalturaCategoryFilter, KalturaCategoryListResponse,
        KalturaUser, KalturaUserFilter, KalturaUserListResponse,
        KalturaUploadToken, KalturaUploadedFileTokenResource
    )
except ImportError:
    # Create mock classes for testing without KalturaClient
    class KalturaMediaEntry:
        def __init__(self, **kwargs):
            # Initialize default attributes
            self.id = None
            self.name = None
            self.description = None
            self.partnerId = None
            self.userId = None
            self.tags = None
            self.status = None
            self.mediaType = None
            self.createdAt = None
            self.updatedAt = None
            self.thumbnailUrl = None
            self.duration = 0
            self.plays = 0
            self.views = 0
            self.width = 0
            self.height = 0
            self.downloadUrl = None
            self.streamUrl = None
            
            # Set provided attributes
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class KalturaMediaEntryFilter:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class KalturaFilterPager:
        def __init__(self, **kwargs):
            self.pageSize = kwargs.get('pageSize', 30)
            self.pageIndex = kwargs.get('pageIndex', 1)
    
    class KalturaMediaEntryListResponse:
        def __init__(self, **kwargs):
            self.objects = kwargs.get('objects', [])
            self.totalCount = kwargs.get('totalCount', 0)
    
    class KalturaMediaType:
        VIDEO = 1
        IMAGE = 2
        AUDIO = 5
        TEXT = 4
        
        def __init__(self, value=None):
            self.value = value
    
    class KalturaMediaEntryStatus:
        PENDING = 1
        READY = 2
        DELETED = 3
        
        def __init__(self, value=None):
            if value is None:
                self.value = self.READY
            elif isinstance(value, int):
                self.value = value
            else:
                # Handle the case where value is another KalturaMediaEntryStatus
                try:
                    self.value = value.value if hasattr(value, 'value') else self.READY
                except:
                    self.value = self.READY
    
    class KalturaCategory:
        def __init__(self, **kwargs):
            # Initialize default attributes
            self.id = None
            self.name = None
            self.description = None
            self.fullName = None
            self.parentId = 0
            self.depth = 1
            self.partnerId = None
            self.tags = None
            self.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
            self.createdAt = None
            self.updatedAt = None
            self.fullIds = ""
            
            # Set provided attributes
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class KalturaCategoryFilter:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class KalturaCategoryListResponse:
        def __init__(self, **kwargs):
            self.objects = kwargs.get('objects', [])
            self.totalCount = kwargs.get('totalCount', 0)
    
    class KalturaUser:
        def __init__(self, **kwargs):
            # Initialize default attributes
            self.id = None
            self.screenName = None
            self.fullName = None
            self.email = None
            self.firstName = None
            self.lastName = None
            self.partnerId = None
            self.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
            self.type = KalturaMediaEntryStatus(0)  # Default type
            self.createdAt = None
            self.updatedAt = None
            self.isAdmin = False
            self.roleIds = ""
            
            # Set provided attributes
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class KalturaUserFilter:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class KalturaUserListResponse:
        def __init__(self, **kwargs):
            self.objects = kwargs.get('objects', [])
            self.totalCount = kwargs.get('totalCount', 0)
            
    class KalturaUploadTokenStatus:
        PENDING = 0
        UPLOADING = 1
        FULL_UPLOAD = 2
        CLOSED = 3
        TIMED_OUT = 4
        DELETED = 5
        
        def __init__(self, value=None):
            if value is None:
                self.value = self.PENDING
            elif isinstance(value, int):
                self.value = value
            else:
                # Handle the case where value is another KalturaUploadTokenStatus
                try:
                    self.value = value.value if hasattr(value, 'value') else self.PENDING
                except:
                    self.value = self.PENDING
        
        def getValue(self):
            return self.value
    
    class KalturaUploadToken:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Initialize required fields if not provided
            if not hasattr(self, 'id'):
                self.id = f"token_{uuid.uuid4().hex}"
            if not hasattr(self, 'status'):
                self.status = KalturaUploadTokenStatus(KalturaUploadTokenStatus.PENDING)
                
    class KalturaUploadedFileTokenResource:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
            # Initialize required fields if not provided
            if not hasattr(self, 'token'):
                self.token = ""

class MockKalturaAPI:
    """Mock implementation of the Kaltura API."""
    
    def __init__(self):
        """Initialize the mock API with sample data."""
        self.media_entries: Dict[str, KalturaMediaEntry] = {}
        self.categories: Dict[int, KalturaCategory] = {}
        self.users: Dict[str, KalturaUser] = {}
        self.next_category_id = 1
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize the mock API with sample data."""
        # Create sample media entries
        for i in range(1, 21):
            entry_id = f"0_sample{i}"
            self.media_entries[entry_id] = KalturaMediaEntry(
                id=entry_id,
                name=f"Sample Media {i}",
                description=f"This is a sample media entry {i} for testing purposes. It contains some longer text to test summarization and context management strategies.",
                partnerId=1,
                userId="admin",
                creatorId="admin",
                tags=f"sample,test,media{i}",
                categories="Sample Category",
                categoryIds="1",
                status=KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY),
                moderationStatus=1,
                createdAt=int(time.time()) - (i * 86400),  # i days ago
                updatedAt=int(time.time()) - (i * 3600),   # i hours ago
                mediaType=KalturaMediaType(KalturaMediaType.VIDEO if i % 3 != 0 else KalturaMediaType.IMAGE),
                duration=i * 60 if i % 3 != 0 else 0,
                plays=i * 100,
                views=i * 150,
                width=1920,
                height=1080,
                msDuration=i * 60 * 1000 if i % 3 != 0 else 0,
                downloadUrl=f"https://example.com/download/{entry_id}",
                streamUrl=f"https://example.com/stream/{entry_id}",
                thumbnailUrl=f"https://example.com/thumbnail/{entry_id}",
                accessControlId=1,
                startDate=None,
                endDate=None,
                referenceId=f"ref_{i}",
                replacingEntryId=None,
                replacedEntryId=None,
                replacementStatus=None,
                partnerSortValue=0,
                conversionProfileId=1,
                rootEntryId=None,
                parentEntryId=None,
                operationAttributes=[],
                entitledUsersEdit="",
                entitledUsersPublish="",
                entitledUsersView="",
                capabilities="",
                templateEntryId=None
            )
        
        # Create sample categories
        for i in range(1, 11):
            category_id = i
            parent_id = 0 if i <= 3 else ((i - 1) % 3) + 1
            depth = 1 if parent_id == 0 else 2
            full_name = f"Category {i}" if parent_id == 0 else f"Category {parent_id}>Category {i}"
            
            self.categories[category_id] = KalturaCategory(
                id=category_id,
                parentId=parent_id,
                depth=depth,
                name=f"Category {i}",
                fullName=full_name,
                partnerId=1,
                entriesCount=i * 5,
                createdAt=int(time.time()) - (i * 86400),  # i days ago
                updatedAt=int(time.time()) - (i * 3600),   # i hours ago
                description=f"This is sample category {i} for testing purposes.",
                tags=f"category,test,sample{i}",
                status=KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY),
                inheritanceType=1,
                privacy=1,
                privacyContext="",
                privacyContexts="",
                membersCount=i * 2,
                pendingMembersCount=i,
                directSubCategoriesCount=0,
                contributionPolicy=1,
                defaultPermissionLevel=1,
                owner="admin",
                directEntitledUsersCount=0,
                referenceId=f"ref_cat_{i}",
                contributionPolicyStatus=1,
                membersCountStatus=1,
                pendingMembersCountStatus=1,
                directSubCategoriesCountStatus=1,
                directEntitledUsersCountStatus=1
            )
            self.next_category_id = category_id + 1
        
        # Create sample users
        for i in range(1, 11):
            user_id = f"user{i}"
            self.users[user_id] = KalturaUser(
                id=user_id,
                partnerId=1,
                screenName=f"User {i}",
                fullName=f"Test User {i}",
                email=f"user{i}@example.com",
                status=KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY),
                createdAt=int(time.time()) - (i * 86400),  # i days ago
                updatedAt=int(time.time()) - (i * 3600),   # i hours ago
                partnerData="",
                indexedPartnerDataInt=0,
                indexedPartnerDataString="",
                storageSize=0,
                language="en",
                lastLoginTime=int(time.time()) - (i * 3600),
                statusUpdatedAt=int(time.time()) - (i * 86400),
                deletedAt=None,
                allowedPartnerIds="",
                allowedPartnerPackages="",
                userMode=0,
                firstName=f"Test{i}",
                lastName=f"User{i}",
                isAdmin=False,
                roleIds="",
                roleNames="",
                isAccountOwner=False,
                password="",
                loginEnabled=True,
                registrationInfo="",
                attendanceInfo="",
                title="",
                company="",
                ksPrivileges="",
                encryptedSeed="",
                isSsoExcluded=False
            )
    
    async def list_media(self, filter_params: Optional[Dict[str, Any]] = None, pager: Optional[Dict[str, int]] = None) -> KalturaMediaEntryListResponse:
        """List media entries based on filter and pager."""
        filter_params = filter_params or {}
        pager = pager or {}
        
        # Apply filters
        filtered_entries = list(self.media_entries.values())
        
        if 'idEqual' in filter_params:
            filtered_entries = [e for e in filtered_entries if e.id == filter_params['idEqual']]
        
        if 'idIn' in filter_params and filter_params['idIn']:
            id_list = filter_params['idIn'].split(',')
            filtered_entries = [e for e in filtered_entries if e.id in id_list]
        
        if 'nameLike' in filter_params and filter_params['nameLike']:
            pattern = re.compile(filter_params['nameLike'], re.IGNORECASE)
            filtered_entries = [e for e in filtered_entries if pattern.search(e.name)]
        
        if 'statusEqual' in filter_params:
            filtered_entries = [e for e in filtered_entries if e.status == filter_params['statusEqual']]
        
        if 'statusIn' in filter_params and filter_params['statusIn']:
            status_list = [int(s) for s in filter_params['statusIn'].split(',')]
            filtered_entries = [e for e in filtered_entries if e.status in status_list]
        
        # Apply paging
        page_size = pager.get('pageSize', 30)
        page_index = pager.get('pageIndex', 1)
        
        start_index = (page_index - 1) * page_size
        end_index = start_index + page_size
        
        paged_entries = filtered_entries[start_index:end_index]
        
        # Create response
        response = KalturaMediaEntryListResponse(
            objects=paged_entries,
            totalCount=len(filtered_entries)
        )
        
        return response
    
    async def get_media_entry(self, entry_id: str) -> KalturaMediaEntry:
        """Get a media entry by ID."""
        if entry_id not in self.media_entries:
            raise Exception(f"Media entry not found: {entry_id}")
        
        return self.media_entries[entry_id]
    
    async def add_media_entry(self, entry: KalturaMediaEntry) -> KalturaMediaEntry:
        """Add a new media entry."""
        # Create a new entry with a unique ID
        new_entry = KalturaMediaEntry()
        
        # Copy attributes from the input entry
        for attr in dir(entry):
            if not attr.startswith('_') and hasattr(entry, attr):
                value = getattr(entry, attr)
                if value is not None:
                    setattr(new_entry, attr, value)
        
        # Set required fields
        new_entry.id = f"0_{uuid.uuid4().hex}"
        new_entry.createdAt = int(time.time())
        new_entry.updatedAt = int(time.time())
        new_entry.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        # Ensure mediaType is properly set
        if not hasattr(new_entry, 'mediaType') or new_entry.mediaType is None:
            new_entry.mediaType = KalturaMediaType(KalturaMediaType.VIDEO)
        elif not hasattr(new_entry.mediaType, 'value'):
            new_entry.mediaType = KalturaMediaType(new_entry.mediaType)
        
        # Add to the media entries dictionary
        self.media_entries[new_entry.id] = new_entry
        
        return new_entry
    
    async def update_media_entry(self, entry_id: str, entry: KalturaMediaEntry) -> KalturaMediaEntry:
        """Update a media entry."""
        if entry_id not in self.media_entries:
            raise Exception(f"Media entry not found: {entry_id}")
        
        # Get the existing entry
        existing_entry = self.media_entries[entry_id]
        
        # Update fields
        for attr in dir(entry):
            if not attr.startswith('_') and hasattr(entry, attr):
                value = getattr(entry, attr)
                if value is not None:
                    setattr(existing_entry, attr, value)
        
        existing_entry.updatedAt = int(time.time())
        
        return existing_entry
    
    async def delete_media_entry(self, entry_id: str) -> None:
        """Delete a media entry."""
        if entry_id not in self.media_entries:
            raise Exception(f"Media entry not found: {entry_id}")
        
        del self.media_entries[entry_id]
    
    async def list_categories(self, filter_params: Optional[Dict[str, Any]] = None, pager: Optional[Dict[str, int]] = None) -> KalturaCategoryListResponse:
        """List categories based on filter and pager."""
        filter_params = filter_params or {}
        pager = pager or {}
        
        # Apply filters
        filtered_categories = list(self.categories.values())
        
        if 'idEqual' in filter_params:
            filtered_categories = [c for c in filtered_categories if c.id == filter_params['idEqual']]
        
        if 'idIn' in filter_params and filter_params['idIn']:
            id_list = [int(i) for i in filter_params['idIn'].split(',')]
            filtered_categories = [c for c in filtered_categories if c.id in id_list]
        
        if 'parentIdEqual' in filter_params:
            filtered_categories = [c for c in filtered_categories if c.parentId == filter_params['parentIdEqual']]
        
        if 'nameLike' in filter_params and filter_params['nameLike']:
            pattern = re.compile(filter_params['nameLike'], re.IGNORECASE)
            filtered_categories = [c for c in filtered_categories if pattern.search(c.name)]
        
        # Apply paging
        page_size = pager.get('pageSize', 30)
        page_index = pager.get('pageIndex', 1)
        
        start_index = (page_index - 1) * page_size
        end_index = start_index + page_size
        
        paged_categories = filtered_categories[start_index:end_index]
        
        # Create response
        response = KalturaCategoryListResponse(
            objects=paged_categories,
            totalCount=len(filtered_categories)
        )
        
        return response
    
    async def get_category(self, category_id: int) -> KalturaCategory:
        """Get a category by ID."""
        if category_id not in self.categories:
            raise Exception(f"Category not found: {category_id}")
        
        return self.categories[category_id]
    
    async def add_category(self, category: KalturaCategory) -> KalturaCategory:
        """Add a new category."""
        # Create a new category with a unique ID
        new_category = KalturaCategory()
        
        # Copy attributes from the input category
        for attr in dir(category):
            if not attr.startswith('_') and hasattr(category, attr):
                value = getattr(category, attr)
                if value is not None:
                    setattr(new_category, attr, value)
        
        # Always set the ID field
        new_category.id = self.next_category_id
        self.next_category_id += 1
        
        new_category.createdAt = int(time.time())
        new_category.updatedAt = int(time.time())
        
        # Ensure status is properly set with a value attribute
        new_category.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        # Set parent-related fields
        if hasattr(new_category, 'parentId') and new_category.parentId and new_category.parentId in self.categories:
            parent = self.categories[new_category.parentId]
            new_category.depth = parent.depth + 1
            new_category.fullName = f"{parent.fullName}>{new_category.name}"
        else:
            new_category.parentId = 0
            new_category.depth = 1
            new_category.fullName = new_category.name
        
        # Make sure fullIds is set
        if not hasattr(new_category, 'fullIds') or new_category.fullIds is None:
            new_category.fullIds = str(new_category.id)
        
        self.categories[new_category.id] = new_category
        
        return new_category
    
    async def update_category(self, category_id: int, category: KalturaCategory) -> KalturaCategory:
        """Update a category."""
        if category_id not in self.categories:
            raise Exception(f"Category not found: {category_id}")
        
        # Get the existing category
        existing_category = self.categories[category_id]
        
        # Update fields
        for attr in dir(category):
            if not attr.startswith('_') and hasattr(category, attr):
                value = getattr(category, attr)
                if value is not None:
                    setattr(existing_category, attr, value)
        
        existing_category.updatedAt = int(time.time())
        
        # Update fullName if name changed
        if hasattr(category, 'name') and category.name:
            existing_category.name = category.name
            if existing_category.parentId and existing_category.parentId in self.categories:
                parent = self.categories[existing_category.parentId]
                existing_category.fullName = f"{parent.fullName}>{existing_category.name}"
            else:
                existing_category.fullName = existing_category.name
        
        return existing_category
    
    async def delete_category(self, category_id: int) -> None:
        """Delete a category."""
        if category_id not in self.categories:
            raise Exception(f"Category not found: {category_id}")
        
        del self.categories[category_id]
    
    async def list_users(self, filter_params: Optional[Dict[str, Any]] = None, pager: Optional[Dict[str, int]] = None) -> KalturaUserListResponse:
        """List users based on filter and pager."""
        filter_params = filter_params or {}
        pager = pager or {}
        
        # Apply filters
        filtered_users = list(self.users.values())
        
        if 'idEqual' in filter_params:
            filtered_users = [u for u in filtered_users if u.id == filter_params['idEqual']]
        
        if 'idIn' in filter_params and filter_params['idIn']:
            id_list = filter_params['idIn'].split(',')
            filtered_users = [u for u in filtered_users if u.id in id_list]
        
        if 'statusEqual' in filter_params:
            filtered_users = [u for u in filtered_users if u.status == filter_params['statusEqual']]
        
        if 'statusIn' in filter_params and filter_params['statusIn']:
            status_list = [int(s) for s in filter_params['statusIn'].split(',')]
            filtered_users = [u for u in filtered_users if u.status in status_list]
        
        if 'screenNameLike' in filter_params and filter_params['screenNameLike']:
            pattern = re.compile(filter_params['screenNameLike'], re.IGNORECASE)
            filtered_users = [u for u in filtered_users if pattern.search(u.screenName)]
        
        if 'emailLike' in filter_params and filter_params['emailLike']:
            pattern = re.compile(filter_params['emailLike'], re.IGNORECASE)
            filtered_users = [u for u in filtered_users if pattern.search(u.email)]
        
        # Apply paging
        page_size = pager.get('pageSize', 30)
        page_index = pager.get('pageIndex', 1)
        
        start_index = (page_index - 1) * page_size
        end_index = start_index + page_size
        
        paged_users = filtered_users[start_index:end_index]
        
        # Create response
        response = KalturaUserListResponse(
            objects=paged_users,
            totalCount=len(filtered_users)
        )
        
        return response
    
    async def get_user(self, user_id: str) -> KalturaUser:
        """Get a user by ID."""
        if user_id not in self.users:
            raise Exception(f"User not found: {user_id}")
        
        return self.users[user_id]
    
    async def add_user(self, user: KalturaUser) -> KalturaUser:
        """Add a new user."""
        # Create a new user
        new_user = KalturaUser()
        
        # Copy attributes from the input user
        for attr in dir(user):
            if not attr.startswith('_') and hasattr(user, attr):
                value = getattr(user, attr)
                if value is not None:
                    setattr(new_user, attr, value)
        
        # Check if ID is set
        if not hasattr(new_user, 'id') or not new_user.id:
            raise Exception("User ID is required")
        
        if new_user.id in self.users:
            raise Exception(f"User already exists: {new_user.id}")
        
        # Set required fields
        new_user.createdAt = int(time.time())
        new_user.updatedAt = int(time.time())
        
        # Ensure status is properly set with a value attribute
        new_user.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        # Ensure type is properly set with a value attribute
        new_user.type = KalturaMediaEntryStatus(0)  # Default type
        
        self.users[new_user.id] = new_user
        
        return new_user
    
    async def update_user(self, user_id: str, user: KalturaUser) -> KalturaUser:
        """Update a user."""
        if user_id not in self.users:
            raise Exception(f"User not found: {user_id}")
        
        # Get the existing user
        existing_user = self.users[user_id]
        
        # Update fields
        for attr in dir(user):
            if not attr.startswith('_') and hasattr(user, attr):
                value = getattr(user, attr)
                if value is not None:
                    setattr(existing_user, attr, value)
        
        existing_user.updatedAt = int(time.time())
        
        return existing_user
    
    async def delete_user(self, user_id: str) -> None:
        """Delete a user."""
        if user_id not in self.users:
            raise Exception(f"User not found: {user_id}")
        
        del self.users[user_id]

class MockKalturaClientWrapper:
    """Mock wrapper for the Kaltura client."""
    
    def __init__(self, config=None):
        """Initialize the mock client wrapper."""
        self.api = MockKalturaAPI()
        self.config = config
        self.session_id = f"mock_session_{uuid.uuid4().hex}"
    
    async def initialize(self):
        """Initialize the client."""
        # Nothing to do for the mock client
        pass
        
    async def ensure_valid_ks(self):
        """Ensure a valid Kaltura Session is available."""
        return self.session_id
    
    def get_service_url(self):
        """Get the Kaltura service URL."""
        return "https://example.com/api_v3"
    
    def get_ks(self):
        """Get the Kaltura Session ID."""
        return self.session_id
    
    async def execute_request(self, service, action, **params):
        """Execute a Kaltura API request."""
        # Map service and action to the appropriate method
        if service == "media":
            if action == "list":
                return await self.list_media(**params)
            elif action == "get":
                return await self.get_media_entry(params.get("entryId"))
            elif action == "add":
                return await self.add_media_entry(**params)
            elif action == "update":
                entry_id = params.get("entryId")
                media_entry = params.get("mediaEntry")
                
                # Extract fields from mediaEntry
                update_params = {}
                if media_entry:
                    for attr in dir(media_entry):
                        if not attr.startswith('_') and hasattr(media_entry, attr):
                            value = getattr(media_entry, attr)
                            if value is not None:
                                update_params[attr] = value
                
                return await self.update_media_entry(entry_id, **update_params)
            elif action == "delete":
                return await self.delete_media_entry(params.get("entryId"))
            elif action == "addContent":
                # Handle addContent action for media
                entry_id = params.get("entryId")
                if entry_id in self.api.media_entries:
                    return self.api.media_entries[entry_id]
                else:
                    raise ValueError(f"Media entry not found: {entry_id}")
        elif service == "uploadToken":
            if action == "add":
                token_id = f"token_{uuid.uuid4().hex}"
                return KalturaUploadToken(id=token_id)
            elif action == "upload":
                token_id = params.get("uploadTokenId")
                return KalturaUploadToken(id=token_id, status="ready")
            elif action == "get":
                token_id = params.get("uploadTokenId")
                # Create a token with FULL_UPLOAD status
                token = KalturaUploadToken(
                    id=token_id,
                    fileName="test.txt",
                    fileSize=1024,
                    uploadedFileSize=1024,
                    status=KalturaUploadTokenStatus.FULL_UPLOAD if hasattr(KalturaUploadTokenStatus, "FULL_UPLOAD") else 2
                )
                # Add a getValue method to the status attribute if it doesn't have one
                if not hasattr(token.status, "getValue"):
                    token.status.getValue = lambda: 2  # FULL_UPLOAD status
                return token
        elif service == "data":
            if action == "add":
                return await self.add_data_entry(**params)
            elif action == "addContent":
                return await self.add_data_content(params.get("entryId"), **params)
            elif action == "get":
                return await self.get_data_entry(params.get("entryId"))
        elif service == "baseEntry":
            if action == "addFromUploadedFile":
                return await self.upload_media(params.get("uploadTokenId"), **params)
        elif service == "category":
            if action == "list":
                return await self.list_categories(**params)
            elif action == "get":
                return await self.get_category(params.get("id"))
            elif action == "add":
                return await self.add_category(**params)
            elif action == "update":
                return await self.update_category(params.get("id"), **params)
            elif action == "delete":
                return await self.delete_category(params.get("id"))
        elif service == "user":
            if action == "list":
                return await self.list_users(**params)
            elif action == "get":
                return await self.get_user(params.get("userId"))
            elif action == "add":
                return await self.add_user(**params)
            elif action == "update":
                return await self.update_user(params.get("userId"), **params)
            elif action == "delete":
                return await self.delete_user(params.get("userId"))
        
        raise ValueError(f"Unknown service or action: {service}.{action}")
    
    async def list_media(self, **kwargs):
        """List media entries."""
        filter_params = {}
        pager = {}
        
        # Extract filter parameters
        for key, value in kwargs.items():
            if key.startswith('filter_'):
                filter_key = key[7:]  # Remove 'filter_' prefix
                filter_params[filter_key] = value
            elif key in ['page_size', 'page']:
                if key == 'page_size':
                    pager['pageSize'] = value
                elif key == 'page':
                    pager['pageIndex'] = value
        
        return await self.api.list_media(filter_params, pager)
    
    async def get_media_entry(self, entry_id):
        """Get a media entry by ID."""
        return await self.api.get_media_entry(entry_id)
    
    async def add_media_entry(self, **kwargs):
        """Add a new media entry."""
        entry = KalturaMediaEntry(**kwargs)
        return await self.api.add_media_entry(entry)
    
    async def update_media_entry(self, entry_id, **kwargs):
        """Update a media entry."""
        if entry_id not in self.api.media_entries:
            raise ValueError(f"Media entry not found: {entry_id}")
            
        # Get the existing entry
        existing_entry = self.api.media_entries[entry_id]
        
        # Update fields directly from kwargs
        for key, value in kwargs.items():
            if hasattr(existing_entry, key) and value is not None:
                setattr(existing_entry, key, value)
        
        # Make sure id is set
        existing_entry.id = entry_id
        existing_entry.updatedAt = int(time.time())
        
        # Ensure status has a value attribute
        if hasattr(existing_entry, 'status') and not hasattr(existing_entry.status, 'value'):
            if isinstance(existing_entry.status, int):
                existing_entry.status = KalturaMediaEntryStatus(existing_entry.status)
            else:
                existing_entry.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        # Ensure mediaType has a value attribute
        if hasattr(existing_entry, 'mediaType') and not hasattr(existing_entry.mediaType, 'value'):
            if isinstance(existing_entry.mediaType, int):
                existing_entry.mediaType = KalturaMediaType(existing_entry.mediaType)
            else:
                existing_entry.mediaType = KalturaMediaType(KalturaMediaType.VIDEO)
        
        return existing_entry
    
    async def delete_media_entry(self, entry_id):
        """Delete a media entry."""
        await self.api.delete_media_entry(entry_id)
        return True
    
    async def upload_media(self, uploadTokenId=None, **kwargs):
        """Upload a media file."""
        # Mock file upload by creating a media entry
        entry = KalturaMediaEntry()
        
        # Extract name if present
        name = kwargs.get('name')
        
        # Set the entry properties from kwargs
        for key, value in kwargs.items():
            if key == 'entry':
                # Handle the case where entry is passed directly
                for attr in dir(value):
                    if not attr.startswith('_') and hasattr(value, attr):
                        val = getattr(value, attr)
                        if val is not None:
                            setattr(entry, attr, val)
            elif hasattr(entry, key):
                setattr(entry, key, value)
        
        # Set required fields
        entry.id = f"0_{uuid.uuid4().hex}"
        entry.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        entry.mediaType = KalturaMediaType(KalturaMediaType.VIDEO)
        entry.createdAt = int(time.time())
        entry.updatedAt = int(time.time())
        
        # Make sure name is set
        if name:
            entry.name = name
        
        # Handle the case where name is in the baseEntry parameter
        if 'baseEntry' in kwargs and hasattr(kwargs['baseEntry'], 'name') and kwargs['baseEntry'].name:
            entry.name = kwargs['baseEntry'].name
        
        # Add additional required fields
        if not hasattr(entry, 'thumbnailUrl') or entry.thumbnailUrl is None:
            entry.thumbnailUrl = ""
        
        # Store in the API's media entries
        self.api.media_entries[entry.id] = entry
        
        return entry
    
    async def list_categories(self, **kwargs):
        """List categories."""
        filter_params = {}
        pager = {}
        
        # Extract filter parameters
        for key, value in kwargs.items():
            if key.startswith('filter_'):
                filter_key = key[7:]  # Remove 'filter_' prefix
                filter_params[filter_key] = value
            elif key in ['page_size', 'page']:
                if key == 'page_size':
                    pager['pageSize'] = value
                elif key == 'page':
                    pager['pageIndex'] = value
        
        return await self.api.list_categories(filter_params, pager)
    
    async def get_category(self, category_id):
        """Get a category by ID."""
        return await self.api.get_category(category_id)
    
    async def add_category(self, category=None, **kwargs):
        """Add a new category."""
        if category is None:
            category = KalturaCategory()
            # Set the category properties from kwargs
            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)
        
        # Handle the case where category is passed directly in kwargs
        if 'category' in kwargs and kwargs['category'] is not None:
            category = kwargs['category']
            
        # Make sure name is set
        if not hasattr(category, 'name') or category.name is None:
            category.name = "Default Category"
            
        return await self.api.add_category(category)
    
    async def update_category(self, category_id, **kwargs):
        """Update a category."""
        # Extract name if present
        name = kwargs.get('name')
        
        # Create category object
        category = KalturaCategory(**kwargs)
        
        # Ensure name is set
        if name:
            category.name = name
            
        return await self.api.update_category(category_id, category)
    
    async def delete_category(self, category_id):
        """Delete a category."""
        await self.api.delete_category(category_id)
        return True
    
    async def list_users(self, **kwargs):
        """List users."""
        filter_params = {}
        pager = {}
        
        # Extract filter parameters
        for key, value in kwargs.items():
            if key.startswith('filter_'):
                filter_key = key[7:]  # Remove 'filter_' prefix
                filter_params[filter_key] = value
            elif key in ['page_size', 'page']:
                if key == 'page_size':
                    pager['pageSize'] = value
                elif key == 'page':
                    pager['pageIndex'] = value
        
        return await self.api.list_users(filter_params, pager)
    
    async def get_user(self, user_id):
        """Get a user by ID."""
        return await self.api.get_user(user_id)
    
    async def add_user(self, user=None, **kwargs):
        """Add a new user."""
        if user is None:
            user = KalturaUser()
            # Set the user properties from kwargs
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
                # Handle special case for id parameter
                elif key == 'id' and not hasattr(user, 'id'):
                    user.id = value
        
        # Handle the case where user is passed directly in kwargs
        if 'user' in kwargs and kwargs['user'] is not None:
            user = kwargs['user']
            
        # Make sure required fields are set
        if not hasattr(user, 'id') or not user.id:
            user.id = f"user_{uuid.uuid4().hex[:8]}"
            
        if not hasattr(user, 'email') or not user.email:
            user.email = f"{user.id}@example.com"
            
        if not hasattr(user, 'fullName') or not user.fullName:
            user.fullName = f"Test User {user.id}"
            
        if not hasattr(user, 'screenName') or not user.screenName:
            user.screenName = user.fullName
            
        return await self.api.add_user(user)
    
    async def update_user(self, user_id, **kwargs):
        """Update a user."""
        # Extract screen_name if present
        screen_name = kwargs.pop('screen_name', None)
        
        # Create user object
        user = KalturaUser(**kwargs)
        
        # Get the result
        result = await self.api.update_user(user_id, user)
        
        # Apply screen_name if provided
        if screen_name:
            result.screenName = screen_name
            
        return result
    
    async def delete_user(self, user_id):
        """Delete a user."""
        await self.api.delete_user(user_id)
        return True
        
    async def add_data_entry(self, dataEntry=None, **kwargs):
        """Add a new data entry."""
        # Create a new data entry with a unique ID
        entry_id = f"0_data_{uuid.uuid4().hex}"
        
        # Create a mock data entry
        data_entry = MagicMock()
        data_entry.id = entry_id
        data_entry.name = dataEntry.name if dataEntry and hasattr(dataEntry, 'name') else kwargs.get('name', 'Mock Data Entry')
        data_entry.description = dataEntry.description if dataEntry and hasattr(dataEntry, 'description') else kwargs.get('description', '')
        data_entry.tags = dataEntry.tags if dataEntry and hasattr(dataEntry, 'tags') else kwargs.get('tags', '')
        data_entry.createdAt = int(time.time())
        data_entry.updatedAt = int(time.time())
        data_entry.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        # Add to the media entries dictionary so it can be found by the update/delete methods
        self.api.media_entries[entry_id] = data_entry
        
        return data_entry
        
    async def add_data_content(self, entry_id, **kwargs):
        """Add content to a data entry."""
        # Create a mock data entry with content
        data_entry = MagicMock()
        data_entry.id = entry_id
        data_entry.name = kwargs.get('name', 'Mock Data Entry')
        data_entry.description = kwargs.get('description', '')
        data_entry.tags = kwargs.get('tags', '')
        data_entry.createdAt = int(time.time())
        data_entry.updatedAt = int(time.time())
        data_entry.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        return data_entry
        
    async def get_data_entry(self, entry_id):
        """Get a data entry by ID."""
        # Create a mock data entry
        data_entry = MagicMock()
        data_entry.id = entry_id
        data_entry.name = 'Mock Data Entry'
        data_entry.description = 'Mock data entry description'
        data_entry.tags = 'mock,data,test'
        data_entry.createdAt = int(time.time())
        data_entry.updatedAt = int(time.time())
        data_entry.status = KalturaMediaEntryStatus(KalturaMediaEntryStatus.READY)
        
        return data_entry
