# Notion to AppFlowy Migration Tool

A comprehensive Python script for migrating content from Notion exports to AppFlowy self-hosted instances. This tool provides time estimation before migration and includes Big O complexity analysis.

## Features

- ✅ **Automated Migration**: Seamlessly migrate Notion exports to AppFlowy
- ⏱️ **Time Estimation**: Get accurate time estimates before starting migration
- 🔬 **Complexity Analysis**: Built-in Big O complexity analysis for performance understanding
- 📊 **Progress Tracking**: Real-time progress reporting during migration
- 🚀 **Dual Import Methods**: Support for both ZIP upload and individual page upload
- 🛡️ **Pre-flight Checks**: Validates connections and files before migration
- 📈 **Detailed Statistics**: Comprehensive migration summary and success rates

## Requirements

- Python 3.7 or higher
- `requests` library
- Access to an AppFlowy self-hosted instance
- Notion export ZIP file

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/AppFlowy-IO/AppFlowy.git
   cd AppFlowy
   ```

2. **Install Python dependencies**:
   ```bash
   pip install requests
   ```

3. **Make the script executable** (Unix/Linux/Mac):
   ```bash
   chmod +x tools/notion_to_appflowy_migration.py
   ```

## How to Export from Notion

1. Open your Notion workspace
2. Click "Settings & members" in the sidebar
3. Go to "Settings" → "Export content"
4. Choose "Export all workspace content"
5. Select format: "Markdown & CSV" (recommended) or "HTML"
6. Click "Export" and download the ZIP file

## Usage

### Basic Usage

```bash
python tools/notion_to_appflowy_migration.py \
    --notion-export /path/to/notion_export.zip \
    --appflowy-url http://localhost:8080 \
    --workspace-id YOUR_WORKSPACE_ID
```

### With Authentication

If your AppFlowy instance requires API key authentication:

```bash
python tools/notion_to_appflowy_migration.py \
    --notion-export /path/to/notion_export.zip \
    --appflowy-url https://appflowy.example.com \
    --workspace-id YOUR_WORKSPACE_ID \
    --api-key YOUR_API_KEY
```

### Individual Page Upload (Fallback Method)

If ZIP import is not supported or fails, use individual page upload:

```bash
python tools/notion_to_appflowy_migration.py \
    --notion-export /path/to/notion_export.zip \
    --appflowy-url http://localhost:8080 \
    --workspace-id YOUR_WORKSPACE_ID \
    --no-zip-import
```

## Command-Line Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--notion-export` | Yes | Path to Notion export ZIP file |
| `--appflowy-url` | Yes | URL of AppFlowy self-hosted instance |
| `--workspace-id` | Yes | AppFlowy workspace ID for import destination |
| `--api-key` | No | API key for authentication (if required) |
| `--no-zip-import` | No | Disable ZIP import and use individual page upload |

## Migration Process

The script follows these steps:

### 1. Pre-Migration Check
- Tests connection to AppFlowy instance
- Validates Notion export file exists
- Verifies all prerequisites are met

### 2. Content Analysis
- Extracts and analyzes the Notion export
- Counts files, pages, and total size
- Provides file type breakdown

### 3. Time Estimation
The script calculates estimated migration time based on:
- **Processing time**: ~0.5 seconds per page
- **Upload time**: ~10 seconds per MB (network-dependent)
- **API overhead**: ~0.2 seconds per request

Example output:
```
⏱️  Time Estimation:
   Estimated time: 5.3 minutes
                   (0.09 hours)

   Breakdown:
      Processing: 25.0s
      Upload: 180.0s
      API overhead: 10.0s
```

### 4. Complexity Analysis
The script displays Big O complexity:
```
🔬 Complexity Analysis:
   Algorithm: O(n + m)
   where:
      n = number of pages (50)
      m = total content size (18874368 bytes)

   Space Complexity: O(1)
   - Streaming processing with minimal memory footprint
   - No recursive structures or deep copying
```

### 5. Migration Execution
- Uploads content to AppFlowy (ZIP method or individual pages)
- Displays real-time progress
- Handles errors gracefully with retry logic

### 6. Summary Report
- Total statistics (files, pages, success rate)
- Performance metrics (duration, average time per page)
- List of any failed items

## Big O Complexity Explained

### Time Complexity: O(n + m)
- **n**: Number of pages in the export
- **m**: Total content size in bytes
- The algorithm scales linearly with input size

Operations breakdown:
- File extraction: O(n) - iterate through all files
- Content parsing: O(m) - read all content
- Upload: O(n) - upload each page
- **Total**: O(n + m), simplified to O(n) when n dominates

### Space Complexity: O(1)
- Uses streaming processing
- Minimal memory footprint
- No recursive data structures
- Files are processed one at a time

## Example Output

```
============================================================
PRE-MIGRATION CHECK
============================================================

1. Testing AppFlowy connection...
   ✓ Connection successful

2. Validating Notion export...
   ✓ Export file found

============================================================
CONTENT ANALYSIS & TIME ESTIMATION
============================================================

Extracting export to /tmp/notion_export_1707858123...

📊 Content Statistics:
   Total files: 127
   Total pages: 50
   Total size: 18.00 MB

   File types breakdown:
      .csv: 5
      .html: 2
      .jpg: 15
      .md: 50
      .png: 55

⏱️  Time Estimation:
   Estimated time: 5.3 minutes
                   (0.09 hours)

   Breakdown:
      Processing: 25.0s
      Upload: 180.0s
      API overhead: 10.0s

🔬 Complexity Analysis:
   Algorithm: O(n + m)
   where:
      n = number of pages (50)
      m = total content size (18874368 bytes)

   Space Complexity: O(1)
   - Streaming processing with minimal memory footprint
   - No recursive structures or deep copying

============================================================
Proceed with migration? (yes/no): yes

============================================================
MIGRATION (ZIP Upload Method)
============================================================

Uploading Notion export ZIP to AppFlowy...
✓ Upload successful! Import ID: abc123-def456-789

============================================================
MIGRATION SUMMARY
============================================================

📈 Statistics:
   Total files: 127
   Total pages: 50
   Processed pages: 50
   Failed items: 0
   Success rate: 100.0%

⏱️  Performance:
   Duration: 185.45 seconds
             (3.09 minutes)
   Average time per page: 3.71s

============================================================
```

## Troubleshooting

### Connection Failed
**Error**: `Failed to connect to AppFlowy instance`

**Solutions**:
- Verify AppFlowy instance is running: `docker ps` or check service status
- Check the URL is correct (include protocol: `http://` or `https://`)
- Ensure no firewall blocking the connection
- Try accessing the health endpoint manually: `curl http://localhost:8080/api/health`

### Export File Not Found
**Error**: `Export file not found`

**Solutions**:
- Verify the file path is correct
- Use absolute path instead of relative path
- Check file permissions (readable)

### ZIP Import Failed
The script automatically falls back to individual page upload if ZIP import fails.

**Manual fallback**:
```bash
python tools/notion_to_appflowy_migration.py \
    --notion-export /path/to/export.zip \
    --appflowy-url http://localhost:8080 \
    --workspace-id YOUR_WORKSPACE_ID \
    --no-zip-import
```

### Memory Issues
If processing very large exports (>1GB):
- The script uses streaming processing (O(1) space complexity)
- Processes files one at a time to minimize memory usage
- If issues persist, split the Notion export into smaller chunks

## Performance Tips

1. **Use ZIP import when possible**: Faster than individual page upload
2. **Local network**: Migrate from a machine on the same network as AppFlowy instance
3. **Batch processing**: For large exports, consider splitting into multiple smaller exports
4. **API rate limiting**: The script includes small delays to avoid overwhelming the server

## Supported Content Types

- ✅ Markdown files (.md)
- ✅ HTML files (.html)
- ✅ CSV databases (.csv)
- ✅ Images (embedded in pages)
- ✅ Attachments (included in export)

## Limitations

1. **API Compatibility**: Script assumes AppFlowy API endpoints - may need adjustment for specific versions
2. **Authentication**: Currently supports API key auth - extend for other auth methods as needed
3. **Notion Features**: Some advanced Notion features may not have direct AppFlowy equivalents
4. **Rate Limiting**: Very large migrations may hit API rate limits

## Advanced Configuration

### Custom Time Estimates

Edit the script to adjust time estimation factors in `estimate_migration_time()`:

```python
# Base time per page (parsing + processing)
base_time = total_pages * 0.5  # Adjust this value

# Upload time (depends on size and network)
upload_time = total_size_mb * 10  # Adjust based on your network speed

# API overhead time
api_overhead = total_pages * 0.2  # Adjust based on server performance
```

### Error Handling

The script includes error handling for:
- Network failures (automatic retry can be added)
- Invalid file formats
- Missing credentials
- API errors

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- **Issues**: Report issues on [GitHub Issues](https://github.com/AppFlowy-IO/AppFlowy/issues)
- **Discussions**: Join [AppFlowy Discord](https://discord.gg/9Q2xaN37tV)
- **Documentation**: See [AppFlowy Documentation](https://docs.appflowy.io/)

## License

This script is part of AppFlowy and is distributed under the AGPLv3 License. See [LICENSE](../LICENSE) for more information.

## Related Resources

- [AppFlowy Documentation](https://docs.appflowy.io/)
- [AppFlowy Self-Hosting Guide](https://appflowy.com/docs/Step-by-step-Self-Hosting-Guide---From-Zero-to-Production)
- [Notion API Documentation](https://developers.notion.com/)
- [Import from Notion Guide](https://docs.appflowy.io/docs/guides/import-from-notion)

## Changelog

### Version 1.0.0 (2024)
- Initial release
- ZIP import support
- Individual page upload fallback
- Time estimation and Big O analysis
- Progress tracking and statistics
- Comprehensive error handling
