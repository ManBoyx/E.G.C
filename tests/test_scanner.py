"""Unit tests for the antivirus scanner module."""
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Mock PyQt5 before importing scanner
import sys
mock_qt_widgets = MagicMock()
mock_qt_core = MagicMock()
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtWidgets'] = mock_qt_widgets
sys.modules['PyQt5.QtCore'] = mock_qt_core

# Provide a real base class for QThread mock
mock_qt_core.QThread = type('QThread', (), {
    '__init__': lambda self, *a, **kw: None,
    'run': lambda self: None,
})
mock_qt_core.pyqtSignal = lambda *a: MagicMock()

from src.antivirus.scanner import (
    ScanThread,
    VIRUS_SIGNATURES,
    QUARANTINE_DIR,
)


class TestScanFile:
    """Tests for ScanThread.scan_file method."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.thread = ScanThread.__new__(ScanThread)
        self.thread.stop_flag = False
        self.thread.infected_files = []
        self.thread.directory = self.tmpdir
        self.thread.scan_type = "Scan rapide"
        self.thread.update_signal = MagicMock()
        self.thread.progress_signal = MagicMock()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_clean_file_returns_false(self):
        """A file without virus signatures should not be flagged."""
        clean_file = Path(self.tmpdir) / "clean.txt"
        clean_file.write_text("This is a perfectly safe file.")
        assert self.thread.scan_file(str(clean_file)) is False

    def test_infected_file_with_eicar_returns_true(self):
        """A file containing the 'eicar' signature should be flagged."""
        infected_file = Path(self.tmpdir) / "infected.txt"
        infected_file.write_bytes(b"some content eicar more content")
        assert self.thread.scan_file(str(infected_file)) is True

    def test_infected_file_with_malicious_returns_true(self):
        """A file containing the 'malicious' signature should be flagged."""
        infected_file = Path(self.tmpdir) / "malware.bin"
        infected_file.write_bytes(b"header malicious payload")
        assert self.thread.scan_file(str(infected_file)) is True

    def test_empty_file_returns_false(self):
        """An empty file should not be flagged."""
        empty_file = Path(self.tmpdir) / "empty.txt"
        empty_file.write_bytes(b"")
        assert self.thread.scan_file(str(empty_file)) is False

    def test_binary_file_without_signature_returns_false(self):
        """A binary file without signatures should not be flagged."""
        bin_file = Path(self.tmpdir) / "data.bin"
        bin_file.write_bytes(os.urandom(16384))
        assert self.thread.scan_file(str(bin_file)) is False

    def test_nonexistent_file_returns_false(self):
        """A non-existent file path should return False (handled gracefully)."""
        assert self.thread.scan_file("/nonexistent/path/file.txt") is False

    def test_large_file_with_signature_in_second_chunk(self):
        """Signature in a later chunk should still be detected."""
        large_file = Path(self.tmpdir) / "large.bin"
        # Write more than one chunk (8192 bytes) before the signature
        content = b"A" * 9000 + b"eicar" + b"B" * 1000
        large_file.write_bytes(content)
        assert self.thread.scan_file(str(large_file)) is True


class TestScanFiles:
    """Tests for ScanThread.scan_files method."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.thread = ScanThread.__new__(ScanThread)
        self.thread.stop_flag = False
        self.thread.infected_files = []
        self.thread.directory = self.tmpdir
        self.thread.scan_type = "Scan rapide"
        self.thread.update_signal = MagicMock()
        self.thread.progress_signal = MagicMock()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_empty_directory_returns_empty_list(self):
        """Scanning an empty directory should return no infected files."""
        result = self.thread.scan_files(self.tmpdir)
        assert result == []

    def test_directory_with_only_clean_files(self):
        """Scanning a directory with only clean files should return empty."""
        for i in range(5):
            (Path(self.tmpdir) / f"file{i}.txt").write_text(f"safe content {i}")
        result = self.thread.scan_files(self.tmpdir)
        assert result == []

    def test_directory_with_infected_file(self):
        """Scanning a directory with an infected file should detect it."""
        clean = Path(self.tmpdir) / "clean.txt"
        clean.write_text("safe content")
        infected = Path(self.tmpdir) / "virus.dat"
        infected.write_bytes(b"contains eicar signature")
        result = self.thread.scan_files(self.tmpdir)
        assert len(result) == 1
        assert "virus.dat" in result[0]

    def test_scan_emits_progress_signals(self):
        """Progress signal should be emitted during scan."""
        (Path(self.tmpdir) / "file.txt").write_text("content")
        self.thread.scan_files(self.tmpdir)
        assert self.thread.progress_signal.emit.called

    def test_stop_flag_halts_scan(self):
        """Setting stop_flag should halt the scan early."""
        for i in range(10):
            (Path(self.tmpdir) / f"file{i}.txt").write_text("safe")
        self.thread.stop_flag = True
        result = self.thread.scan_files(self.tmpdir)
        assert result == []

    def test_nested_directories(self):
        """Scanner should recursively scan subdirectories."""
        subdir = Path(self.tmpdir) / "subdir" / "deep"
        subdir.mkdir(parents=True)
        (subdir / "infected.bin").write_bytes(b"malicious code here")
        result = self.thread.scan_files(self.tmpdir)
        assert len(result) == 1


class TestQuarantineFile:
    """Tests for ScanThread.quarantine_file method."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.thread = ScanThread.__new__(ScanThread)
        self.thread.stop_flag = False
        self.thread.infected_files = []
        self.thread.update_signal = MagicMock()
        self.thread.progress_signal = MagicMock()

    def teardown_method(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_quarantine_moves_file(self):
        """Quarantine should move the file to the .quarantine directory."""
        file_path = Path(self.tmpdir) / "virus.exe"
        file_path.write_bytes(b"eicar test")
        self.thread.quarantine_file(str(file_path))
        assert not file_path.exists()
        quarantine_path = Path(self.tmpdir) / QUARANTINE_DIR / "virus.exe"
        assert quarantine_path.exists()

    def test_quarantine_creates_directory(self):
        """Quarantine should create the .quarantine directory if needed."""
        file_path = Path(self.tmpdir) / "malware.bin"
        file_path.write_bytes(b"malicious")
        qdir = Path(self.tmpdir) / QUARANTINE_DIR
        assert not qdir.exists()
        self.thread.quarantine_file(str(file_path))
        assert qdir.exists()

    def test_quarantine_emits_signal(self):
        """Quarantine should emit update signal on success."""
        file_path = Path(self.tmpdir) / "bad.txt"
        file_path.write_bytes(b"eicar")
        self.thread.quarantine_file(str(file_path))
        assert self.thread.update_signal.emit.called

    def test_quarantine_nonexistent_file_handles_error(self):
        """Quarantine should handle non-existent file gracefully."""
        self.thread.quarantine_file("/nonexistent/file.txt")
        # Should emit an error message, not crash
        assert self.thread.update_signal.emit.called


class TestStopFlag:
    """Tests for ScanThread.stop method."""

    def test_stop_sets_flag(self):
        """stop() should set stop_flag to True."""
        thread = ScanThread.__new__(ScanThread)
        thread.stop_flag = False
        thread.stop()
        assert thread.stop_flag is True


class TestVirusSignatures:
    """Tests for virus signature constants."""

    def test_signatures_are_bytes(self):
        """All signatures should be bytes objects."""
        for sig in VIRUS_SIGNATURES:
            assert isinstance(sig, bytes)

    def test_known_signatures_present(self):
        """Known signatures should be in the set."""
        assert b"eicar" in VIRUS_SIGNATURES
        assert b"malicious" in VIRUS_SIGNATURES
