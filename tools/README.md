# Notion to AppFlowy Migration Tool

This directory contains tools for migrating content from Notion to AppFlowy.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Export from Notion**:
   - In Notion: Settings & Members → Settings → Export content
   - Choose "Export all workspace content"
   - Format: "Markdown & CSV" (recommended)
   - Download the ZIP file

3. **Run the migration**:
   ```bash
   python notion_to_appflowy_migration.py \
       --notion-export /path/to/notion_export.zip \
       --appflowy-url http://localhost:8080 \
       --workspace-id YOUR_WORKSPACE_ID
   ```

## Files

- **`notion_to_appflowy_migration.py`** - Main migration script
- **`test_migration.py`** - Test suite with mock data
- **`requirements.txt`** - Python dependencies
- **`README_MIGRATION.md`** - Comprehensive documentation

## Testing

Run the test suite to verify everything works:

```bash
python test_migration.py
```

This will:
- Create a mock Notion export
- Test the parser and analysis
- Verify time estimation
- Display complexity analysis
- Confirm all functionality works

## Documentation

See [README_MIGRATION.md](README_MIGRATION.md) for:
- Detailed usage instructions
- Command-line arguments
- Time estimation details
- Big O complexity analysis
- Troubleshooting guide
- Performance tips

## Support

- Issues: [GitHub Issues](https://github.com/AppFlowy-IO/AppFlowy/issues)
- Discord: [AppFlowy Discord](https://discord.gg/9Q2xaN37tV)
- Docs: [AppFlowy Documentation](https://docs.appflowy.io/)
