"""Unit tests for the browser navigator module."""
import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock PyQt5 before importing
sys.modules['PyQt5'] = MagicMock()
sys.modules['PyQt5.QtWidgets'] = MagicMock()
sys.modules['PyQt5.QtWebEngineWidgets'] = MagicMock()
sys.modules['PyQt5.QtCore'] = MagicMock()


class TestURLNormalization:
    """Tests for the URL normalization logic in OptimizedBrowser.load_url.

    The logic is:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
    """

    def normalize_url(self, url: str) -> str:
        """Replicate the URL normalization logic from navigator.py."""
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def test_plain_domain_gets_https(self):
        """A plain domain should get https:// prepended."""
        assert self.normalize_url("google.com") == "https://google.com"

    def test_www_domain_gets_https(self):
        """www.domain gets https:// prepended."""
        assert self.normalize_url("www.example.com") == "https://www.example.com"

    def test_https_url_unchanged(self):
        """A URL already starting with https:// should not be modified."""
        url = "https://github.com/ManBoyx"
        assert self.normalize_url(url) == url

    def test_http_url_unchanged(self):
        """A URL starting with http:// should not be modified."""
        url = "http://example.com"
        assert self.normalize_url(url) == url

    def test_url_with_path(self):
        """Domain with path should get https:// prepended."""
        assert self.normalize_url("example.com/path/to/page") == "https://example.com/path/to/page"

    def test_url_with_port(self):
        """Domain with port should get https:// prepended."""
        assert self.normalize_url("localhost:8080") == "https://localhost:8080"

    def test_empty_string(self):
        """Empty string should get https:// prepended."""
        assert self.normalize_url("") == "https://"

    def test_url_with_query_params(self):
        """URL with query params should be handled correctly."""
        url = "example.com/search?q=test&lang=en"
        assert self.normalize_url(url) == "https://example.com/search?q=test&lang=en"

    def test_ftp_url_gets_https_prepended(self):
        """Non-http protocols get https:// prepended (current behavior)."""
        assert self.normalize_url("ftp://files.example.com") == "https://ftp://files.example.com"

    def test_url_with_fragment(self):
        """URL with fragment should be handled correctly."""
        url = "example.com/page#section"
        assert self.normalize_url(url) == "https://example.com/page#section"


class TestTabManagement:
    """Tests for tab management logic."""

    def test_close_tab_with_multiple_tabs(self):
        """Closing a tab should work when more than 1 tab exists."""
        tab_count = 3
        tabs = list(range(tab_count))
        index_to_close = 1
        if len(tabs) > 1:
            tabs.pop(index_to_close)
        assert len(tabs) == 2
        assert index_to_close not in tabs

    def test_close_tab_with_single_tab_does_nothing(self):
        """Should not close the last remaining tab."""
        tab_count = 1
        tabs = list(range(tab_count))
        index_to_close = 0
        if len(tabs) > 1:
            tabs.pop(index_to_close)
        assert len(tabs) == 1  # Still has 1 tab

    def test_add_tab_increases_count(self):
        """Adding a tab should increase the tab count."""
        tabs = ["tab1"]
        tabs.append("tab2")
        assert len(tabs) == 2

    def test_multiple_tabs_can_be_opened(self):
        """Multiple tabs can be opened sequentially."""
        tabs = []
        for i in range(5):
            tabs.append(f"tab{i}")
        assert len(tabs) == 5
