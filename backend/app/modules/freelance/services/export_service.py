"""
RIGHT FIT Core — Freelance Leads Spreadsheet Export Service (Excel & CSV)
Version: 1.0.0
Produces structured, professional .xlsx and .csv files with DDE formula injection security defense.
"""

from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)


class FreelanceExportService:
    """Generates styled Excel (.xlsx) and clean CSV spreadsheets for freelance leads."""

    @staticmethod
    def sanitize_spreadsheet_cell(val: Any) -> Any:
        """
        DDE / CSV Formula Injection Defense.
        Cells starting with =, @, +, -, or tab (\\t) are escaped with a leading single quote.
        """
        if val is None:
            return ""
        if isinstance(val, (int, float, bool)):
            return val
        val_str = str(val)
        if val_str and val_str[0] in ("=", "@", "+", "-", "\t"):
            return f"'{val_str}"
        return val_str

    @classmethod
    def generate_excel(cls, opportunities: List[Any]) -> bytes:
        """
        Converts a list of FreelanceOpportunityRecord instances or dicts into a polished Excel (.xlsx) workbook.
        Applies auto-column width, professional header styling, and cell sanitization.
        """
        sc = cls.sanitize_spreadsheet_cell

        rows = []
        for opp in opportunities:
            # Handle both SQLAlchemy objects and dicts
            def get_val(key: str, default: Any = "") -> Any:
                if isinstance(opp, dict):
                    return opp.get(key, default)
                return getattr(opp, key, default)

            # Determine website gap status
            is_broken = bool(get_val("is_broken_website", False))
            website = get_val("website") or ""
            if not website:
                web_status = "No Website (Prime Candidate)"
            elif is_broken:
                web_status = "Broken Website (Repair Required)"
            else:
                web_status = "Active Website"

            # Clean phone and format whatsapp link
            phone_raw = get_val("phone") or ""
            phone_digits = "".join(c for c in phone_raw if c.isdigit())
            whatsapp_url = f"https://wa.me/{phone_digits}" if phone_digits else ""

            # Discovered date formatted
            discovered = get_val("discovered_at")
            if isinstance(discovered, datetime):
                disc_str = discovered.strftime("%Y-%m-%d %H:%M")
            elif discovered:
                disc_str = str(discovered)[:16]
            else:
                disc_str = ""

            rows.append({
                "Business Name": sc(get_val("business_name")),
                "Category / Niche": sc(get_val("service_category")),
                "City": sc(get_val("city")),
                "Website Status": sc(web_status),
                "Priority": sc(get_val("priority", "MEDIUM")),
                "Fit Score (%)": sc(get_val("relevance_score", 85.0)),
                "Verified Email": sc(get_val("email")),
                "Direct Phone": sc(phone_raw),
                "WhatsApp Link": sc(whatsapp_url),
                "Website URL": sc(website),
                "Google Rating": sc(get_val("rating", 0.0)),
                "Reviews Count": sc(get_val("reviews_count", 0)),
                "Instagram": sc(get_val("instagram")),
                "Facebook": sc(get_val("facebook")),
                "LinkedIn": sc(get_val("linkedin")),
                "Twitter / X": sc(get_val("twitter")),
                "Recommended Pitch": sc(get_val("suggested_service")),
                "Discovered At": sc(disc_str),
            })

        df = pd.DataFrame(rows)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Freelance Leads")

            worksheet = writer.sheets["Freelance Leads"]

            # Header styling: Deep Indigo fill, White Bold text
            header_fill = PatternFill(start_color="312E81", end_color="312E81", fill_type="solid")
            header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style="thin", color="E2E8F0"),
                right=Side(style="thin", color="E2E8F0"),
                top=Side(style="thin", color="E2E8F0"),
                bottom=Side(style="thin", color="E2E8F0"),
            )

            for col_idx in range(1, len(df.columns) + 1):
                cell = worksheet.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=False)

            # Auto-adjust column width
            for idx, col in enumerate(df.columns):
                max_len = max(
                    df[col].apply(lambda x: len(str(x)) if x is not None and not pd.isna(x) else 0).max(),
                    len(col),
                ) + 3
                max_len = min(max(max_len, 12), 45)  # Constrain between 12 and 45 chars
                worksheet.column_dimensions[get_column_letter(idx + 1)].width = max_len

            # Set border and alignment for data cells
            for row in worksheet.iter_rows(min_row=2, max_row=len(rows) + 1, min_col=1, max_col=len(df.columns)):
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(vertical="center")

        output.seek(0)
        return output.getvalue()

    @classmethod
    def generate_csv(cls, opportunities: List[Any]) -> bytes:
        """Generates clean UTF-8 CSV with BOM for immediate spreadsheet loading."""
        sc = cls.sanitize_spreadsheet_cell
        rows = []
        for opp in opportunities:
            def get_val(key: str, default: Any = "") -> Any:
                if isinstance(opp, dict):
                    return opp.get(key, default)
                return getattr(opp, key, default)

            is_broken = bool(get_val("is_broken_website", False))
            website = get_val("website") or ""
            web_status = "No Website" if not website else ("Broken Website" if is_broken else "Active Website")

            rows.append({
                "Business Name": sc(get_val("business_name")),
                "Category": sc(get_val("service_category")),
                "City": sc(get_val("city")),
                "Website Status": sc(web_status),
                "Priority": sc(get_val("priority", "MEDIUM")),
                "Fit Score": sc(get_val("relevance_score", 85.0)),
                "Email": sc(get_val("email")),
                "Phone": sc(get_val("phone")),
                "Website": sc(website),
                "Rating": sc(get_val("rating", 0.0)),
                "Reviews": sc(get_val("reviews_count", 0)),
                "Instagram": sc(get_val("instagram")),
                "Facebook": sc(get_val("facebook")),
                "LinkedIn": sc(get_val("linkedin")),
                "Twitter": sc(get_val("twitter")),
                "Recommended Service": sc(get_val("suggested_service")),
            })

        df = pd.DataFrame(rows)
        # utf-8-sig adds BOM so Excel opens Hindi/special characters correctly without encoding artifacts
        return df.to_csv(index=False).encode("utf-8-sig")
