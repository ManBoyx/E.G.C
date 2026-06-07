# Optimized Programs

This directory contains optimized versions of all programs from the E.G.C repository.

## Performance Improvements

### 1. **Antivirus Scanner** (`antivirus_scanner.py`)
- ✅ Reduced memory usage with streaming file reads
- ✅ Better exception handling
- ✅ Faster scan using chunks instead of full file reads
- ✅ Removed redundant global variables
- ✅ Type hints for better code clarity
- ✅ Proper thread cleanup

### 2. **Photo Editor** (`photo_editor.py`)
- ✅ Simplified UI without complex animations
- ✅ Reduced memory footprint
- ✅ Faster image operations
- ✅ Removed redundant code
- ✅ Better resource management

### 3. **Web Browser** (`web_browser.py`)
- ✅ Lightweight implementation
- ✅ Efficient tab management
- ✅ Removed unnecessary plugins
- ✅ Faster startup

### 4. **Sound Amplifier** (`sound_amplifier.py`)
- ✅ Proper error handling for missing dependencies
- ✅ Better signal clipping to prevent audio distortion
- ✅ Simplified UI

## Key Optimizations Applied

1. **Code Structure**: Removed code duplication, organized imports
2. **Memory Management**: Used generators, streaming, and efficient data structures
3. **Performance**: Optimized loops, reduced I/O operations, better resource cleanup
4. **Error Handling**: Added try-except blocks, proper exception messages
5. **Type Safety**: Added type hints for better code quality
6. **Resource Cleanup**: Proper thread stopping and resource disposal

## Dependencies

```bash
pip install PyQt5 pillow numpy sounddevice PyQtWebEngine
```

## Running the Programs

```bash
python antivirus_scanner.py
python photo_editor.py
python web_browser.py
python sound_amplifier.py
```
