#!/usr/bin/env python3
"""Classify a package on old Android without exporting the device's app list.

Uses Android 5-compatible "pm list packages FILTER". No app contents, phone
identifiers, accounts, or raw package-manager output are recorded.
"""
import re

PACKAGE = "com.facebook.orca"


def parse_package_list(stdout, stderr="", returncode=0, package=PACKAGE):
    """Return True if installed, False if absent, None if inconclusive.

    Missing packages often make "pm path" exit nonzero on old ROMs.
    "pm list packages FILTER" with success and empty output means absent.
    """
    if returncode != 0:
        return None
    out = (stdout or "").strip()
    err = (stderr or "").strip()
    if err or re.search(r"(?i)(unknown command|error:|exception|permission denial)", out):
        return None
    if not out:
        return False
    lines = out.splitlines()
    if not all(re.fullmatch(r"package:[A-Za-z0-9_.]+", line.strip()) for line in lines):
        return None
    return package in {line.strip().split(":", 1)[1] for line in lines}


def installed_package(adb, command, package=PACKAGE):
    """Call the read-only package listing with caller-supplied ADB executor."""
    result = command(adb, "shell", "pm", "list", "packages", package)
    if result is None:
        return None
    return parse_package_list(result.stdout, result.stderr, result.returncode, package)
