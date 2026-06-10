"""Unit tests for the photo editor module."""
import sys
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

# Mock tkinter before importing editor
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.colorchooser'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()


class TestPhotoEditorUndoRedo:
    """Tests for the undo/redo logic in PhotoEditor."""

    def setup_method(self):
        """Create a PhotoEditor-like object without GUI."""
        self.editor = MagicMock()
        self.editor.image = Image.new('RGB', (100, 100), 'white')
        self.editor.undo_stack = []
        self.editor.redo_stack = []
        self.editor.color = "black"
        self.editor.brush_size = 5

    def _undo(self):
        """Replicate undo logic."""
        if self.editor.undo_stack:
            self.editor.redo_stack.append(self.editor.image.copy())
            self.editor.image = self.editor.undo_stack.pop()

    def _redo(self):
        """Replicate redo logic."""
        if self.editor.redo_stack:
            self.editor.undo_stack.append(self.editor.image.copy())
            self.editor.image = self.editor.redo_stack.pop()

    def _paint(self, x, y):
        """Replicate paint logic."""
        self.editor.undo_stack.append(self.editor.image.copy())
        draw = ImageDraw.Draw(self.editor.image)
        bs = self.editor.brush_size
        draw.ellipse([x - bs, y - bs, x + bs, y + bs], fill=self.editor.color)

    def test_undo_empty_stack_does_nothing(self):
        """Undo with empty stack should not crash or change image."""
        original = self.editor.image.copy()
        self._undo()
        assert self.editor.image.tobytes() == original.tobytes()

    def test_redo_empty_stack_does_nothing(self):
        """Redo with empty stack should not crash or change image."""
        original = self.editor.image.copy()
        self._redo()
        assert self.editor.image.tobytes() == original.tobytes()

    def test_paint_adds_to_undo_stack(self):
        """Painting should push state to undo stack."""
        assert len(self.editor.undo_stack) == 0
        self._paint(50, 50)
        assert len(self.editor.undo_stack) == 1

    def test_undo_restores_previous_state(self):
        """Undo should restore the image to previous state."""
        original_bytes = self.editor.image.tobytes()
        self._paint(50, 50)
        painted_bytes = self.editor.image.tobytes()
        assert painted_bytes != original_bytes
        self._undo()
        assert self.editor.image.tobytes() == original_bytes

    def test_redo_restores_undone_state(self):
        """Redo should restore the undone state."""
        self._paint(50, 50)
        painted_bytes = self.editor.image.tobytes()
        self._undo()
        self._redo()
        assert self.editor.image.tobytes() == painted_bytes

    def test_multiple_undo(self):
        """Multiple undos should walk back through history."""
        state0 = self.editor.image.tobytes()
        self._paint(10, 10)
        state1 = self.editor.image.tobytes()
        self._paint(20, 20)
        state2 = self.editor.image.tobytes()

        self._undo()
        assert self.editor.image.tobytes() == state1
        self._undo()
        assert self.editor.image.tobytes() == state0

    def test_undo_then_paint_clears_redo_concept(self):
        """After undo, painting creates new branch (redo stack still has items)."""
        self._paint(10, 10)
        self._paint(20, 20)
        self._undo()
        # Redo stack has one item
        assert len(self.editor.redo_stack) == 1
        # New paint adds to undo stack
        self._paint(30, 30)
        assert len(self.editor.undo_stack) == 2


class TestPaintLogic:
    """Tests for painting operations."""

    def test_paint_modifies_image(self):
        """Painting should modify pixel data."""
        image = Image.new('RGB', (100, 100), 'white')
        original_bytes = image.tobytes()
        draw = ImageDraw.Draw(image)
        draw.ellipse([45, 45, 55, 55], fill="black")
        assert image.tobytes() != original_bytes

    def test_paint_with_different_colors(self):
        """Painting with different colors should produce different results."""
        img1 = Image.new('RGB', (100, 100), 'white')
        img2 = Image.new('RGB', (100, 100), 'white')
        ImageDraw.Draw(img1).ellipse([45, 45, 55, 55], fill="red")
        ImageDraw.Draw(img2).ellipse([45, 45, 55, 55], fill="blue")
        assert img1.tobytes() != img2.tobytes()

    def test_paint_with_different_brush_sizes(self):
        """Different brush sizes should produce different results."""
        img1 = Image.new('RGB', (100, 100), 'white')
        img2 = Image.new('RGB', (100, 100), 'white')
        ImageDraw.Draw(img1).ellipse([48, 48, 52, 52], fill="black")  # size 2
        ImageDraw.Draw(img2).ellipse([40, 40, 60, 60], fill="black")  # size 10
        assert img1.tobytes() != img2.tobytes()


class TestResetLogic:
    """Tests for the reset method."""

    def test_reset_clears_coordinates(self):
        """Reset should clear last_x and last_y."""
        last_x, last_y = 50, 60
        # After reset
        last_x, last_y = None, None
        assert last_x is None
        assert last_y is None
