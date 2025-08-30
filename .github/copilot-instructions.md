# GameWorld AI Agent Instructions

## Project Overview
GameWorld is a **server-driven** multiplayer game platform with ENet networking. The server generates all UI dynamically (menus, forms) and sends them to a wxPython client. Key principle: **client is a dumb terminal** - all game logic, validation, and state management lives on the server.

## Architecture & Core Patterns

### Server-Driven Everything
- **Dynamic Menus**: Server builds menu items with `{id, action, label}` and sends via `MENU_UPDATE` messages
- **Dynamic Forms**: Server sends complete form definitions via `FORM_DEFINITION` messages  
- **Single-Use IDs**: Menu item IDs are consumed on first use, with 500ms debounce per user
- **State Authority**: All game state, validation, and business logic lives in `server/`

### Network Architecture
**ENet with 8-channel separation** (see `CHANNEL_ARCHITECTURE.md`):
- Channel 0: Control (auth, critical)
- Channel 1: Chat  
- Channel 2: Game state
- Channel 3: Game actions
- Channel 4: Room events
- Channel 5: Menu/UI updates
- Channel 6: Audio (unreliable)
- Channel 7: Broadcasts

### Game Service Pattern
Games follow modular architecture in `server/games/[game]/`:
```
service.py      # Main game service class with menu builders
state.py        # Game state models  
logic.py        # Pure game logic functions
validation.py   # Input validation
messages.py     # Game-specific message types
```

Example from Ludo: `LudoGameService.build_base_menu_model()` returns menu items based on game state.

## Development Workflows

### Testing Patterns
- **Mock-heavy testing**: Use `unittest.mock.Mock` for dependencies
- **Pytest with fixtures**: Run tests with `python -m pytest -q`
- **Integration tests**: Test full game flows with mock clients
- **Task runner**: Use VS Code tasks or `python main.py test`

### Build & Packaging
- **Client builds**: `packaging/build_client.py` (PyInstaller) or `packaging/build_client_nuitka.py`
- **Dev launcher**: `python main.py server|client|test|setup`
- **Virtual env**: Uses `.venv/` - auto-created by build scripts
- **Dependencies**: See `requirements.txt` - core is `pyenet`, `wxpython`, `pygame`

### Audio System
**Multi-backend audio** with sound key mapping:
```python
# Play sound by key (maps to actual file paths)
self.emit_buffer([user_id], "text", sound='ludo_move', buffer_name='game')
```
Backends: Bass Audio (high quality) → PyGame → Fallback (text-only)

## Critical Implementation Details

### Message Protocol
Centralized in `shared/protocol/messages.py`:
- **MessageType enum**: Single source of truth for all message types
- **Message class**: Handles serialization/deserialization
- **Helper factories**: `create_menu_update_message()`, `create_form_definition_message()`, etc.

### Database Patterns
- **SQLite with models**: Each feature has dedicated model file (e.g., `quick_message_models.py`)
- **Migration strategy**: Use `ALTER TABLE ... ADD COLUMN` with try/catch for new fields
- **Connection pattern**: Use `with sqlite3.connect(db_path) as conn:` for transactions

### Error Handling
- **Clean error messages**: Avoid technical jargon in user-facing errors
- **Logging**: Use `get_logger()` from `server/utils/logging.py`
- **Client announcements**: Use `announce_error()`, `announce_success()` for accessibility

### Internationalization
- **Gettext-based i18n**: Use `tr(lang, 'key', default='fallback')` pattern
- **Tool**: `python tools/i18n.py all` for extract→merge→compile workflow
- **Arabic plurals**: 6 forms handled automatically in translation system

## Quick Reference

### Key Commands
```bash
python main.py server           # Start server
python main.py client           # Start client  
python -m pytest -q            # Run tests
python tools/i18n.py all       # Update translations
packaging/build_client.cmd     # Build Windows .exe
```

### Critical Files
- `server/server.py` - Main server entry point
- `shared/protocol/messages.py` - Message protocol definitions
- `client/network/client_manager.py` - ENet client with auto-reconnection
- `server/games/ludo/service.py` - Complete game service example
- `server/handlers/` - Request handlers for auth, rooms, games

### Common Patterns
- **Menu builders**: Return `List[Dict[str, Any]]` with `{id, action, label}`
- **Form handlers**: Process `FORM_SUBMIT` messages and return success/error
- **Game actions**: Validate → Update state → Broadcast menu updates
- **Sound integration**: Include `sound='key'` in buffer/success messages
- **Client mocking**: Use `Mock` objects with `user_id`, `is_authenticated` attributes

Always prioritize **server authority** - the client should never make game decisions, only display what the server tells it to show.
