# A2A Inspector Tools

This folder contains tools and documentation for working with the A2A (Agent-to-Agent) Inspector.

## Files

- **setup_inspector.sh** - Script to set up and run the A2A Inspector locally
- **A2A_INSPECTOR_GUIDE.md** - Complete guide for using the A2A Inspector to debug and test agents
- **A2A_LOGGING_GUIDE.md** - Guide for viewing and analyzing agent logs

## What is A2A Inspector?

The A2A Inspector is a debugging and testing tool for Agent-to-Agent communication. It allows you to:
- Inspect agent communications in real-time
- Debug agent behavior and responses
- Test deployed agents interactively
- View detailed logs and traces

## Quick Start

1. Run the setup script:
   ```bash
   cd tools/a2a-inspector
   ./setup_inspector.sh
   ```

2. Open your browser to the URL shown (typically http://localhost:5001)

3. Connect to your deployed agents and start testing!

For detailed instructions, see [A2A_INSPECTOR_GUIDE.md](./A2A_INSPECTOR_GUIDE.md).
