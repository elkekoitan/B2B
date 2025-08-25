"""
Mock database client for agent orchestrator - Development mode
This file provides mock implementations of Supabase functionality for development
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

class MockSupabaseResponse:
    """Mock Supabase response object"""
    
    def __init__(self, data: Any, count: Optional[int] = None):
        self.data = data if isinstance(data, list) else [data] if data is not None else []
        self.count = count

class MockSupabaseQuery:
    """Mock Supabase query builder"""
    
    def __init__(self, table_name: str, mock_db: Dict[str, List[Dict]]):
        self.table_name = table_name
        self.mock_db = mock_db
        self.filters = []
        self.order_by_field = None
        self.order_desc = False
        self.limit_count = None
        self.offset_count = 0
        self.count_mode = False
        self.single_mode = False
    
    def select(self, fields: str = '*', count: Optional[str] = None):
        if count:
            self.count_mode = True
        return self
    
    def eq(self, field: str, value: Any):
        self.filters.append(('eq', field, value))
        return self
    
    def neq(self, field: str, value: Any):
        self.filters.append(('neq', field, value))
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
            elif filter_type == 'neq':
                data = [item for item in data if item.get(field) != value]
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
    """Mock Supabase client for agent orchestrator development"""
    
    def __init__(self):
        self.mock_db = {}
        # Initialize with some sample data
        self._initialize_sample_data()
        logger.info("Initialized mock Supabase client for agents")
    
    def _initialize_sample_data(self):
        """Initialize with some sample data for testing"""
        # Sample suppliers
        self.mock_db['suppliers'] = [
            {
                'id': 'supplier-1',
                'name': 'TechCorp Suppliers',
                'email': 'contact@techcorp.com',
                'phone': '+1-555-0101',
                'categories': ['electronics', 'technology'],
                'verified': True,
                'rating': 4.5,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            },
            {
                'id': 'supplier-2',
                'name': 'Industrial Solutions Ltd',
                'email': 'info@industrial-solutions.com',
                'phone': '+1-555-0102',
                'categories': ['machinery', 'industrial'],
                'verified': True,
                'rating': 4.2,
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00'
            }
        ]
        
        # Sample RFQs
        self.mock_db['rfqs'] = []
        
        # Sample offers
        self.mock_db['offers'] = []
    
    def table(self, table_name: str):
        """Get table reference"""
        return MockSupabaseTable(table_name, self.mock_db)

def create_client(supabase_url: str, supabase_key: str):
    """Create mock Supabase client"""
    logger.info(f"Creating mock Supabase client (ignoring URL: {supabase_url})")
    return MockSupabaseClient()

# Mock the supabase module for agents
def get_mock_client():
    """Get mock Supabase client for agents"""
    return MockSupabaseClient()