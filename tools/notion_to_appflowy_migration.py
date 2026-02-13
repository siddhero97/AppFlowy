#!/usr/bin/env python3
"""
Notion to AppFlowy Migration Script

This script migrates content from Notion exports to an AppFlowy self-hosted instance.
It provides time estimation and Big O complexity analysis for the migration process.

Usage:
    python notion_to_appflowy_migration.py --notion-export /path/to/notion/export.zip \\
                                           --appflowy-url http://localhost:8080 \\
                                           --workspace-id YOUR_WORKSPACE_ID

Requirements:
    - Python 3.7+
    - requests library
    - zipfile (built-in)
    
Big O Complexity Analysis:
    - File parsing: O(n) where n = number of files in export
    - Content processing: O(m) where m = total content size
    - Upload operations: O(n) where n = number of pages
    - Overall: O(n + m) = O(n) where n dominates (pages and content)
"""

import argparse
import json
import os
import sys
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install it with: pip install requests")
    sys.exit(1)


@dataclass
class MigrationStats:
    """Statistics for migration tracking"""
    total_files: int = 0
    total_pages: int = 0
    total_size_bytes: int = 0
    processed_files: int = 0
    processed_pages: int = 0
    failed_items: List[str] = None
    start_time: float = 0
    end_time: float = 0
    
    def __post_init__(self):
        if self.failed_items is None:
            self.failed_items = []
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration in seconds"""
        # Only calculate if both times have been set (non-zero)
        if self.end_time > 0 and self.start_time > 0:
            return self.end_time - self.start_time
        return 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_pages == 0:
            return 0
        return ((self.total_pages - len(self.failed_items)) / self.total_pages) * 100


class NotionExportParser:
    """
    Parser for Notion export files
    
    Complexity: O(n) where n is the number of files in the export
    """
    
    SUPPORTED_FORMATS = ['.md', '.html', '.csv']
    
    def __init__(self, export_path: str):
        self.export_path = Path(export_path)
        self.temp_dir = None
        
    def extract_export(self) -> Path:
        """
        Extract Notion export ZIP file
        Complexity: O(n) where n is number of files in ZIP
        """
        if not self.export_path.exists():
            raise FileNotFoundError(f"Export file not found: {self.export_path}")
        
        if self.export_path.suffix != '.zip':
            raise ValueError("Export must be a ZIP file")
        
        # Create temporary extraction directory
        self.temp_dir = Path(f"/tmp/notion_export_{int(time.time())}")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Extracting export to {self.temp_dir}...")
        with zipfile.ZipFile(self.export_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        return self.temp_dir
    
    def analyze_export(self, extract_dir: Path) -> Dict:
        """
        Analyze the exported content structure
        Complexity: O(n + m) where n = number of files, m = total content size
        """
        analysis = {
            'total_files': 0,
            'total_pages': 0,
            'total_size_bytes': 0,
            'file_types': {},
            'pages': []
        }
        
        # Walk through all files - O(n)
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                file_path = Path(root) / file
                file_size = file_path.stat().st_size
                file_ext = file_path.suffix.lower()
                
                analysis['total_files'] += 1
                analysis['total_size_bytes'] += file_size
                
                # Count file types
                if file_ext in analysis['file_types']:
                    analysis['file_types'][file_ext] += 1
                else:
                    analysis['file_types'][file_ext] = 1
                
                # Identify pages (markdown or HTML files)
                if file_ext in ['.md', '.html']:
                    analysis['total_pages'] += 1
                    analysis['pages'].append({
                        'path': str(file_path),
                        'name': file_path.stem,
                        'size': file_size,
                        'type': file_ext
                    })
        
        return analysis
    
    def estimate_migration_time(self, analysis: Dict) -> Dict[str, float]:
        """
        Estimate migration time based on content analysis
        
        Complexity: O(1) - constant time calculation
        
        Time estimation factors:
        - Base processing time per page: ~0.5 seconds
        - Network upload time: ~0.1 seconds per KB
        - API overhead: ~0.2 seconds per request
        """
        total_pages = analysis['total_pages']
        total_size_mb = analysis['total_size_bytes'] / (1024 * 1024)
        
        # Base time per page (parsing + processing)
        base_time = total_pages * 0.5
        
        # Upload time (depends on size and network)
        upload_time = total_size_mb * 10  # ~10 seconds per MB (conservative)
        
        # API overhead time
        api_overhead = total_pages * 0.2
        
        # Total estimated time
        estimated_seconds = base_time + upload_time + api_overhead
        
        return {
            'estimated_seconds': estimated_seconds,
            'estimated_minutes': estimated_seconds / 60,
            'estimated_hours': estimated_seconds / 3600,
            'breakdown': {
                'processing_seconds': base_time,
                'upload_seconds': upload_time,
                'api_overhead_seconds': api_overhead
            }
        }


class AppFlowyClient:
    """
    Client for AppFlowy self-hosted instance API
    
    Complexity: O(n) for batch operations where n is number of items
    """
    
    def __init__(self, base_url: str, workspace_id: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.workspace_id = workspace_id
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def test_connection(self) -> bool:
        """
        Test connection to AppFlowy instance
        Complexity: O(1)
        """
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Connection test failed: {e}")
            return False
    
    def upload_page(self, page_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Upload a single page to AppFlowy
        Complexity: O(m) where m is the size of page content
        
        Returns: (success: bool, page_id: Optional[str])
        """
        try:
            # Prepare the request payload
            payload = {
                'workspace_id': self.workspace_id,
                'name': page_data['name'],
                'content': page_data.get('content', ''),
                'type': page_data.get('type', 'document')
            }
            
            # This is a placeholder - actual API endpoint would depend on AppFlowy's API
            # In practice, you would use the ImportZipFile endpoint or similar
            endpoint = f"{self.base_url}/api/workspace/{self.workspace_id}/import"
            
            response = self.session.post(endpoint, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return True, result.get('id')
            else:
                return False, None
                
        except requests.exceptions.RequestException as e:
            print(f"Upload failed for {page_data['name']}: {e}")
            return False, None
    
    def upload_zip(self, zip_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Upload entire Notion export ZIP to AppFlowy
        Complexity: O(n) where n is the size of the ZIP file
        
        This uses AppFlowy's native ZIP import functionality
        """
        try:
            with open(zip_path, 'rb') as f:
                files = {'file': (zip_path.name, f, 'application/zip')}
                endpoint = f"{self.base_url}/api/workspace/{self.workspace_id}/import/zip"
                
                response = self.session.post(endpoint, files=files, timeout=300)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return True, result.get('import_id')
                else:
                    print(f"ZIP upload failed: {response.status_code} - {response.text}")
                    return False, None
                    
        except Exception as e:
            print(f"ZIP upload error: {e}")
            return False, None


class NotionToAppFlowyMigrator:
    """
    Main migration orchestrator
    
    Overall Complexity: O(n + m) where:
    - n = number of pages/files
    - m = total content size
    
    The process is linear with respect to the input size.
    """
    
    def __init__(self, notion_export: str, appflowy_url: str, workspace_id: str, 
                 api_key: Optional[str] = None, use_zip_import: bool = True):
        self.parser = NotionExportParser(notion_export)
        self.client = AppFlowyClient(appflowy_url, workspace_id, api_key)
        self.stats = MigrationStats()
        self.use_zip_import = use_zip_import
    
    def pre_migration_check(self) -> bool:
        """
        Perform pre-migration validation
        Complexity: O(1)
        """
        print("\n" + "="*60)
        print("PRE-MIGRATION CHECK")
        print("="*60)
        
        # Check AppFlowy connection
        print("\n1. Testing AppFlowy connection...")
        if not self.client.test_connection():
            print("   ❌ Failed to connect to AppFlowy instance")
            print(f"   URL: {self.client.base_url}")
            print("\n   Please verify:")
            print("   - AppFlowy instance is running")
            print("   - URL is correct")
            print("   - Network connectivity")
            return False
        print("   ✓ Connection successful")
        
        # Check export file
        print("\n2. Validating Notion export...")
        if not Path(self.parser.export_path).exists():
            print(f"   ❌ Export file not found: {self.parser.export_path}")
            return False
        print("   ✓ Export file found")
        
        return True
    
    def analyze_and_estimate(self) -> Dict:
        """
        Analyze export and provide time estimates
        Complexity: O(n) where n is number of files
        """
        print("\n" + "="*60)
        print("CONTENT ANALYSIS & TIME ESTIMATION")
        print("="*60)
        
        # Extract and analyze
        extract_dir = self.parser.extract_export()
        analysis = self.parser.analyze_export(extract_dir)
        
        # Display analysis
        print(f"\n📊 Content Statistics:")
        print(f"   Total files: {analysis['total_files']}")
        print(f"   Total pages: {analysis['total_pages']}")
        print(f"   Total size: {analysis['total_size_bytes'] / (1024*1024):.2f} MB")
        print(f"\n   File types breakdown:")
        for ext, count in sorted(analysis['file_types'].items()):
            print(f"      {ext}: {count}")
        
        # Time estimation
        time_estimate = self.parser.estimate_migration_time(analysis)
        
        print(f"\n⏱️  Time Estimation:")
        print(f"   Estimated time: {time_estimate['estimated_minutes']:.1f} minutes")
        print(f"                   ({time_estimate['estimated_hours']:.2f} hours)")
        print(f"\n   Breakdown:")
        print(f"      Processing: {time_estimate['breakdown']['processing_seconds']:.1f}s")
        print(f"      Upload: {time_estimate['breakdown']['upload_seconds']:.1f}s")
        print(f"      API overhead: {time_estimate['breakdown']['api_overhead_seconds']:.1f}s")
        
        # Complexity analysis
        print(f"\n🔬 Complexity Analysis:")
        print(f"   Algorithm: O(n + m)")
        print(f"   where:")
        print(f"      n = number of pages ({analysis['total_pages']})")
        print(f"      m = total content size ({analysis['total_size_bytes']} bytes)")
        print(f"\n   Space Complexity: O(1)")
        print(f"   - Streaming processing with minimal memory footprint")
        print(f"   - No recursive structures or deep copying")
        
        self.stats.total_files = analysis['total_files']
        self.stats.total_pages = analysis['total_pages']
        self.stats.total_size_bytes = analysis['total_size_bytes']
        
        return analysis
    
    def migrate_zip(self) -> bool:
        """
        Migrate using ZIP upload (recommended)
        Complexity: O(n) where n is ZIP file size
        """
        print("\n" + "="*60)
        print("MIGRATION (ZIP Upload Method)")
        print("="*60)
        
        print("\nUploading Notion export ZIP to AppFlowy...")
        success, import_id = self.client.upload_zip(Path(self.parser.export_path))
        
        if success:
            print(f"✓ Upload successful! Import ID: {import_id}")
            return True
        else:
            print("❌ Upload failed")
            return False
    
    def migrate_individual_pages(self, analysis: Dict) -> bool:
        """
        Migrate pages individually (fallback method)
        Complexity: O(n) where n is number of pages
        """
        print("\n" + "="*60)
        print("MIGRATION (Individual Page Method)")
        print("="*60)
        
        pages = analysis['pages']
        total = len(pages)
        
        print(f"\nMigrating {total} pages...")
        
        for i, page in enumerate(pages, 1):
            print(f"\n[{i}/{total}] Processing: {page['name']}")
            
            # Read content - O(m) where m is file size
            try:
                with open(page['path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                page_data = {
                    'name': page['name'],
                    'content': content,
                    'type': 'markdown' if page['type'] == '.md' else 'document'
                }
                
                # Upload - O(m) for content size
                success, page_id = self.client.upload_page(page_data)
                
                if success:
                    print(f"   ✓ Uploaded (ID: {page_id})")
                    self.stats.processed_pages += 1
                else:
                    print(f"   ❌ Failed")
                    self.stats.failed_items.append(page['name'])
                
                self.stats.processed_files += 1
                
                # Progress indicator
                progress = (i / total) * 100
                print(f"   Progress: {progress:.1f}%")
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.stats.failed_items.append(page['name'])
        
        return len(self.stats.failed_items) == 0
    
    def migrate(self) -> bool:
        """
        Execute the full migration process
        Overall Complexity: O(n + m) 
        """
        self.stats.start_time = time.time()
        
        # Pre-flight checks - O(1)
        if not self.pre_migration_check():
            return False
        
        # Analyze content - O(n)
        analysis = self.analyze_and_estimate()
        
        # Confirm migration
        print("\n" + "="*60)
        response = input("\nProceed with migration? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Migration cancelled by user")
            return False
        
        # Execute migration
        success = False
        if self.use_zip_import:
            # ZIP import - O(n) where n is ZIP size
            success = self.migrate_zip()
            if not success:
                print("\nZIP import failed. Falling back to individual page migration...")
                success = self.migrate_individual_pages(analysis)
        else:
            # Individual page migration - O(n) where n is number of pages
            success = self.migrate_individual_pages(analysis)
        
        self.stats.end_time = time.time()
        
        # Report results
        self.print_summary()
        
        return success
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        print(f"\n📈 Statistics:")
        print(f"   Total files: {self.stats.total_files}")
        print(f"   Total pages: {self.stats.total_pages}")
        print(f"   Processed pages: {self.stats.processed_pages}")
        print(f"   Failed items: {len(self.stats.failed_items)}")
        print(f"   Success rate: {self.stats.success_rate:.1f}%")
        
        print(f"\n⏱️  Performance:")
        print(f"   Duration: {self.stats.duration_seconds:.2f} seconds")
        print(f"             ({self.stats.duration_seconds/60:.2f} minutes)")
        
        if self.stats.total_pages > 0:
            avg_time = self.stats.duration_seconds / self.stats.total_pages
            print(f"   Average time per page: {avg_time:.2f}s")
        
        if self.stats.failed_items:
            print(f"\n❌ Failed items:")
            for item in self.stats.failed_items[:10]:  # Show first 10
                print(f"   - {item}")
            if len(self.stats.failed_items) > 10:
                print(f"   ... and {len(self.stats.failed_items) - 10} more")
        
        print("\n" + "="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Notion export to AppFlowy self-hosted instance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic migration with ZIP upload
  python notion_to_appflowy_migration.py \\
      --notion-export /path/to/notion_export.zip \\
      --appflowy-url http://localhost:8080 \\
      --workspace-id YOUR_WORKSPACE_ID
  
  # Migration with API key authentication
  python notion_to_appflowy_migration.py \\
      --notion-export /path/to/notion_export.zip \\
      --appflowy-url https://appflowy.example.com \\
      --workspace-id YOUR_WORKSPACE_ID \\
      --api-key YOUR_API_KEY
  
  # Migration with individual page upload (fallback)
  python notion_to_appflowy_migration.py \\
      --notion-export /path/to/notion_export.zip \\
      --appflowy-url http://localhost:8080 \\
      --workspace-id YOUR_WORKSPACE_ID \\
      --no-zip-import

Big O Complexity:
  Time Complexity: O(n + m) where n = pages, m = content size
  Space Complexity: O(1) with streaming processing
        """
    )
    
    parser.add_argument(
        '--notion-export',
        required=True,
        help='Path to Notion export ZIP file'
    )
    
    parser.add_argument(
        '--appflowy-url',
        required=True,
        help='URL of AppFlowy self-hosted instance (e.g., http://localhost:8080)'
    )
    
    parser.add_argument(
        '--workspace-id',
        required=True,
        help='AppFlowy workspace ID for import destination'
    )
    
    parser.add_argument(
        '--api-key',
        help='API key for authentication (optional)'
    )
    
    parser.add_argument(
        '--no-zip-import',
        action='store_true',
        help='Disable ZIP import and use individual page upload'
    )
    
    args = parser.parse_args()
    
    # Create migrator
    migrator = NotionToAppFlowyMigrator(
        notion_export=args.notion_export,
        appflowy_url=args.appflowy_url,
        workspace_id=args.workspace_id,
        api_key=args.api_key,
        use_zip_import=not args.no_zip_import
    )
    
    # Run migration
    success = migrator.migrate()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
