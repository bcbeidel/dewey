# Context System - Dewey Plugin Development

This repository contains **Dewey**, a context optimization plugin for Claude Code.

## What is Dewey?

Dewey is a Claude Code plugin that helps you intelligently manage, analyze, and optimize your context files using LLM-based analysis. It uses your existing Claude Code session - no additional API keys or costs required.

## Quick Start

### Install the Plugin

```bash
# Add the dewey marketplace
/plugin marketplace add bcbeidel/dewey

# Install the dewey plugin
/plugin install dewey

# Run the setup script to install Python dependencies
cd ~/.claude/plugins/dewey && ./setup.sh
```

**Note**: The setup script installs the Python package that powers the analysis features. You only need to run this once after installation.

### Use Commands

Once installed, you can use dewey commands in your Claude Code sessions:

```
/dewey:analyze .
/dewey:split large-file.md
```

### Development Setup

For local development:

```bash
# Clone the repository
git clone https://github.com/bcbeidel/dewey.git
cd dewey

# Create symlink to plugins directory
ln -s "$(pwd)/dewey" ~/.claude/plugins/dewey

# Restart Claude Code
```

## Documentation

- **[Plugin README](dewey/README.md)** - Complete plugin documentation
- **[Implementation Plan](IMPLEMENTATION_PLAN.md)** - Development roadmap

## Plugin Structure

```
dewey/
├── .claude-plugin/plugin.json    # Plugin manifest
├── commands/                      # User-invoked commands
├── src/dewey/                     # Python implementation
├── tests/                         # Test suite
└── README.md                      # Plugin documentation
```

## Development Status

**Version**: 0.0.1 (Early Development)

- ✅ Phase 0: Foundation complete
- 🔄 Phase 1: Core commands in progress
- 📋 Phase 2-3: Planned

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for details.

## Project Files

- `dewey/` - Plugin implementation
- `IMPLEMENTATION_PLAN.md` - Development roadmap v2.0
- `README.md` - This file

---

**For full plugin documentation, see [dewey/README.md](dewey/README.md)**
