"""Data models for gdlex-inspector scan results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FileEntry:
    path: str
    size: int
    category: str = "other"
    risk_level: str = "low"
    risk_message: str = ""
    last_modified: Optional[float] = None
    warning: Optional[str] = None


@dataclass
class DirectoryEntry:
    path: str
    size: int
    file_count: int = 0
    category: str = "other"
    risk_level: str = "low"
    risk_message: str = ""
    warning: Optional[str] = None


@dataclass
class ExtensionSummary:
    extension: str
    total_size: int
    file_count: int


@dataclass
class CategorySummary:
    category: str
    total_size: int
    file_count: int
    risk_level: str = "low"


@dataclass
class ScanIssue:
    path: str
    error: str


@dataclass
class ScanResult:
    root_path: str
    total_size: int = 0
    total_files: int = 0
    total_dirs: int = 0
    top_files: list[FileEntry] = field(default_factory=list)
    top_dirs: list[DirectoryEntry] = field(default_factory=list)
    extensions: list[ExtensionSummary] = field(default_factory=list)
    categories: list[CategorySummary] = field(default_factory=list)
    issues: list[ScanIssue] = field(default_factory=list)
    scan_timestamp: Optional[str] = None
    platform_info: dict = field(default_factory=dict)
    backend_used: str = "python"
    mount_info: dict = field(default_factory=dict)
    volume_usage: dict = field(default_factory=dict)
    scan_scope_warning: Optional[str] = None
