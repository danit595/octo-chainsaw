"""Color palette, fonts, and theme helpers."""

from __future__ import annotations

ACCENTS = {
    "violet": {"primary": "#8B5CF6", "primary_hover": "#7C3AED", "glow": "#A78BFA"},
    "cyan": {"primary": "#06B6D4", "primary_hover": "#0891B2", "glow": "#22D3EE"},
    "emerald": {"primary": "#10B981", "primary_hover": "#059669", "glow": "#34D399"},
    "rose": {"primary": "#F43F5E", "primary_hover": "#E11D48", "glow": "#FB7185"},
    "amber": {"primary": "#F59E0B", "primary_hover": "#D97706", "glow": "#FBBF24"},
}


def palette(theme: str, accent: str) -> dict[str, str]:
    """Return a color palette for a given theme + accent combination."""
    accent_colors = ACCENTS.get(accent, ACCENTS["violet"])
    if theme == "light":
        base = {
            "bg": "#F8FAFC",
            "surface": "#FFFFFF",
            "surface_alt": "#F1F5F9",
            "border": "#E2E8F0",
            "text": "#0F172A",
            "text_muted": "#64748B",
            "success": "#16A34A",
            "warning": "#D97706",
            "danger": "#DC2626",
        }
    else:
        base = {
            "bg": "#0B0E14",
            "surface": "#13171F",
            "surface_alt": "#1A1F2B",
            "border": "#252C3A",
            "text": "#E6EAF2",
            "text_muted": "#8893A7",
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
        }
    return {**base, **accent_colors}


FONT_HEADING = ("Segoe UI Variable", 22, "bold")
FONT_SUBHEADING = ("Segoe UI Variable", 14, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_MUTED = ("Segoe UI", 11)
FONT_MONO = ("JetBrains Mono", 12)
FONT_LARGE_NUMBER = ("Segoe UI Variable", 32, "bold")
