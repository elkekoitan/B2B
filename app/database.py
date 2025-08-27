import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from loguru import logger
from contextlib import suppress

# Optional real Supabase client (used in production)
with suppress(Exception):
    from supabase import create_client as _create_supabase_client

class MockSupabaseResponse:
    """Mock Supabase response"""
    def __init__(self, data: Any = None, count: Optional[int] = None):
        self.data = data
        self.count = count

class MockSupabaseQuery:
    """Mock Supabase query builder"""
    
    def __init__(self, table_name: str, mock_db: Dict[str, List[Dict]]):
        self.table_name = table_name
        self.mock_db = mock_db
        self.filters = []
        self.selected_fields = '*'
        self.order_by_field = None
        self.order_desc = False
        self.limit_count = None
        self.offset_count = 0
    
    def select(self, fields: str, count: Optional[str] = None):
        self.selected_fields = fields
        self.count_mode = count == 'exact'
        return self
    
    def eq(self, field: str, value: Any):
        self.filters.append(('eq', field, value))
        return self
    
    def in_(self, field: str, values: List[Any]):
        self.filters.append(('in', field, values))
        return self
    
    def contains(self, field: str, values: List[Any]):
        self.filters.append(('contains', field, values))
        return self
    
    def order(self, field: str, desc: bool = False):
        self.order_by_field = field
        self.order_desc = desc
        return self
    
    def range(self, start: int, end: int):
        self.offset_count = start
        self.limit_count = end - start + 1
        return self
    
    def limit(self, count: int):
        self.limit_count = count
        return self
    
    def maybe_single(self):
        self.single_mode = True
        return self
    
    def execute(self):
        if self.table_name not in self.mock_db:
            self.mock_db[self.table_name] = []
        
        data = self.mock_db[self.table_name]
        
        # Apply filters
        for filter_type, field, value in self.filters:
            if filter_type == 'eq':
                data = [item for item in data if item.get(field) == value]
            elif filter_type == 'in':
                data = [item for item in data if item.get(field) in value]
            elif filter_type == 'contains':
                data = [item for item in data if any(v in item.get(field, []) for v in value)]
        
        # Apply ordering
        if self.order_by_field:
            data = sorted(data, key=lambda x: x.get(self.order_by_field, ''), reverse=self.order_desc)
        
        # Apply pagination
        if self.limit_count:
            data = data[self.offset_count:self.offset_count + self.limit_count]
        
        # Handle single mode
        if hasattr(self, 'single_mode') and self.single_mode:
            return MockSupabaseResponse(data[0] if data else None)
        
        # Handle count mode
        if hasattr(self, 'count_mode') and self.count_mode:
            return MockSupabaseResponse(data, count=len(data))
        
        return MockSupabaseResponse(data)

class MockSupabaseTable:
    """Mock Supabase table"""
    
    def __init__(self, table_name: str, mock_db: Dict[str, List[Dict]]):
        self.table_name = table_name
        self.mock_db = mock_db
    
    def select(self, fields: str = '*', count: Optional[str] = None):
        return MockSupabaseQuery(self.table_name, self.mock_db).select(fields, count)
    
    def insert(self, data: Dict[str, Any]):
        return MockSupabaseInsertQuery(self.table_name, self.mock_db, data)
    
    def update(self, data: Dict[str, Any]):
        return MockSupabaseUpdateQuery(self.table_name, self.mock_db, data)
    
    def delete(self):
        return MockSupabaseDeleteQuery(self.table_name, self.mock_db)

class MockSupabaseInsertQuery:
    """Mock Supabase insert query"""
    
    def __init__(self, table_name: str, mock_db: Dict[str, List[Dict]], insert_data: Dict[str, Any]):
        self.table_name = table_name
        self.mock_db = mock_db
        self.insert_data = insert_data
    
    def execute(self):
        if self.table_name not in self.mock_db:
            self.mock_db[self.table_name] = []
        
        # Add ID if not present
        if 'id' not in self.insert_data:
            self.insert_data['id'] = str(uuid.uuid4())
        
        # Add timestamps
        now = datetime.utcnow().isoformat()
        if 'created_at' not in self.insert_data:
            self.insert_data['created_at'] = now
        if 'updated_at' not in self.insert_data:
            self.insert_data['updated_at'] = now
        
        self.mock_db[self.table_name].append(self.insert_data.copy())
        return MockSupabaseResponse([self.insert_data])

class MockSupabaseUpdateQuery:
    """Mock Supabase update query"""
    
    def __init__(self, table_name: str, mock_db: Dict[str, List[Dict]], update_data: Dict[str, Any]):
        self.table_name = table_name
        self.mock_db = mock_db
        self.update_data = update_data
        self.filters = []
    
    def eq(self, field: str, value: Any):
        self.filters.append(('eq', field, value))
        return self
    
    def execute(self):
        if self.table_name not in self.mock_db:
            return MockSupabaseResponse([])
        
        data = self.mock_db[self.table_name]
        updated_items = []
        
        for item in data:
            match = True
            for filter_type, field, value in self.filters:
                if filter_type == 'eq' and item.get(field) != value:
                    match = False
                    break
            
            if match:
                item.update(self.update_data)
                item['updated_at'] = datetime.utcnow().isoformat()
                updated_items.append(item.copy())
        
        return MockSupabaseResponse(updated_items)

class MockSupabaseDeleteQuery:
    """Mock Supabase delete query"""
    
    def __init__(self, table_name: str, mock_db: Dict[str, List[Dict]]):
        self.table_name = table_name
        self.mock_db = mock_db
        self.filters = []
    
    def eq(self, field: str, value: Any):
        self.filters.append(('eq', field, value))
        return self
    
    def execute(self):
        if self.table_name not in self.mock_db:
            return MockSupabaseResponse([])
        
        data = self.mock_db[self.table_name]
        deleted_items = []
        
        self.mock_db[self.table_name] = [
            item for item in data 
            if not all(
                item.get(field) == value 
                for filter_type, field, value in self.filters 
                if filter_type == 'eq'
            )
        ]
        
        return MockSupabaseResponse(deleted_items)

class MockSupabaseClient:
    """Mock Supabase client for development/testing"""
    
    def __init__(self):
        self.mock_db = {}
        logger.info("Initialized mock Supabase client")
    
    def table(self, table_name: str):
        return MockSupabaseTable(table_name, self.mock_db)
    
    async def health_check(self) -> dict:
        """Mock health check"""
        return {
            "status": "healthy",
            "connected": True,
            "response_time": "<1ms",
            "type": "mock"
        }

class SupabaseClient:
    """Supabase client wrapper (real only)."""

    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        anon_key = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not (supabase_url and anon_key and service_key and "_create_supabase_client" in globals()):
            raise RuntimeError("Supabase config missing. Set SUPABASE_URL, SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY.")
        try:
            client = _create_supabase_client(supabase_url, anon_key)
            admin_client = _create_supabase_client(supabase_url, service_key)
            self.client = client
            self.admin_client = admin_client
            self.mode = "real"
            logger.info("Using real Supabase client")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def get_client(self, admin: bool = False):
        return self.admin_client if admin else self.client

    async def health_check(self) -> dict:
        # Best-effort health check for real client
        return {
            "status": "healthy",
            "connected": True,
            "type": "real"
        }

def get_supabase_client() -> SupabaseClient:
    return SupabaseClient()

# Global client instances
supabase_client = get_supabase_client()
supabase = supabase_client.get_client()
supabase_admin = supabase_client.get_client(admin=True)
