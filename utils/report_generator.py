import os
import json
import time
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, HRFlowable
)

from utils.evidence_manager import EvidenceManager


_RISK_HEX = {
    "NORMAL":   "#7f8c8d",
    "LOW":      "#27ae60",
    "MEDIUM":   "#e67e22",
    "HIGH":     "#e74c3c",
    "CRITICAL": "#c0392b",
}

_RISK_PRIORITY = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


class ReportGenerator:
    """Generates report.json and report.pdf from EvidenceManager at session end."""

    def __init__(self, evidence_manager: EvidenceManager,
                 session_start: float, candidate: str = "Unknown"):
        self.evidence_manager = evidence_manager
        self.session_start    = session_start
        self.session_end      = time.time()
        self.candidate        = candidate
        self.reports_dir      = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate(self):
        evidence = self.evidence_manager.get_all()
        summary  = self.evidence_manager.get_summary()
        summary["overall_risk"] = self._overall_risk(summary)

        self._write_json(evidence, summary)
        self._write_pdf(evidence, summary)

    # ── JSON ────────────────────────────────────────────────

    def _write_json(self, evidence, summary):
        duration = self.session_end - self.session_start
        data = {
            "candidate":        self.candidate,
            "session_start":    datetime.fromtimestamp(self.session_start).strftime("%Y-%m-%d %H:%M:%S"),
            "session_end":      datetime.fromtimestamp(self.session_end).strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": round(duration, 1),
            "summary":          summary,
            "events":           evidence,
        }
        path = os.path.join(self.reports_dir, "report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"[Report] JSON → {path}")

    # ── PDF ─────────────────────────────────────────────────

    def _write_pdf(self, evidence, summary):
        path = os.path.join(self.reports_dir, "report.pdf")
        doc  = SimpleDocTemplate(
            path, pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm,   bottomMargin=2*cm
        )
        doc.build(self._build_story(evidence, summary))
        print(f"[Report] PDF  → {path}")

    def _build_story(self, evidence, summary):
        styles   = getSampleStyleSheet()
        story    = []
        duration = self.session_end - self.session_start
        overall  = summary.get("overall_risk", "NORMAL")
        risk_hex = _RISK_HEX.get(overall, "#7f8c8d")

        # ── Header ──────────────────────────────────────────
        story.append(Paragraph("AI INTERVIEW PROCTOR", styles["Title"]))
        story.append(Paragraph("Candidate Assessment Report", styles["Heading2"]))
        story.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor("#003366")))
        story.append(Spacer(1, 0.4*cm))

        # ── Interview Summary table ──────────────────────────
        story.append(Paragraph("INTERVIEW SUMMARY", styles["Heading2"]))
        mins, secs = int(duration // 60), int(duration % 60)

        summary_rows = [
            ["Candidate",     self.candidate],
            ["Session Start", datetime.fromtimestamp(self.session_start).strftime("%Y-%m-%d %H:%M:%S")],
            ["Session End",   datetime.fromtimestamp(self.session_end).strftime("%Y-%m-%d %H:%M:%S")],
            ["Duration",      f"{mins}m {secs}s"],
            ["Total Events",  str(summary["total_events"])],
            ["Overall Risk",  Paragraph(
                f'<font color="{risk_hex}"><b>{overall}</b></font>',
                styles["Normal"]
            )],
        ]
        story.append(self._simple_table(summary_rows, col_widths=[5*cm, 11*cm]))
        story.append(Spacer(1, 0.5*cm))

        # ── Behaviour Statistics table ───────────────────────
        story.append(Paragraph("BEHAVIOUR STATISTICS", styles["Heading2"]))
        by_type = summary.get("by_type", {})

        if by_type:
            header = [
                Paragraph("<b>Behaviour</b>", styles["Normal"]),
                Paragraph("<b>Events</b>",    styles["Normal"]),
                Paragraph("<b>Peak Risk</b>", styles["Normal"]),
            ]
            stat_rows = [header]
            for btype, count in by_type.items():
                risks     = [e["risk_level"] for e in evidence if e["event_type"] == btype]
                peak_risk = next((r for r in _RISK_PRIORITY if r in risks), "LOW")
                hex_c     = _RISK_HEX.get(peak_risk, "#7f8c8d")
                stat_rows.append([
                    btype.replace("_", " "),
                    str(count),
                    Paragraph(f'<font color="{hex_c}"><b>{peak_risk}</b></font>', styles["Normal"]),
                ])
            t = Table(stat_rows, colWidths=[9*cm, 2.5*cm, 4.5*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#003366")),
                ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
                ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ("PADDING",        (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f5f5f5")]),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("No events recorded.", styles["Normal"]))

        story.append(Spacer(1, 0.5*cm))

        # ── Chronological Timeline ───────────────────────────
        story.append(Paragraph("CHRONOLOGICAL TIMELINE", styles["Heading2"]))
        story.append(HRFlowable(width="100%", thickness=0.5,
                                color=colors.HexColor("#cccccc")))

        for entry in evidence:
            risk  = entry["risk_level"]
            hex_c = _RISK_HEX.get(risk, "#7f8c8d")
            story.append(Spacer(1, 0.3*cm))

            story.append(Paragraph(
                f'<b>{entry["timestamp"]}</b>  ·  '
                f'{entry["event_type"].replace("_", " ")}  ·  '
                f'{entry["duration"]}s  ·  '
                f'<font color="{hex_c}"><b>{risk}</b></font>',
                styles["Normal"]
            ))
            story.append(Paragraph(entry["description"], styles["Normal"]))

            # Embed screenshot inline if it was captured
            screenshot = entry.get("screenshot")
            if screenshot and os.path.exists(screenshot):
                story.append(Spacer(1, 0.2*cm))
                story.append(Image(screenshot, width=10*cm, height=7.5*cm))

            story.append(Spacer(1, 0.2*cm))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                    color=colors.HexColor("#eeeeee")))

        story.append(Spacer(1, 0.5*cm))

        # ── Overall Assessment ───────────────────────────────
        story.append(Paragraph("OVERALL ASSESSMENT", styles["Heading2"]))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#003366")))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(self._assessment(evidence, summary), styles["Normal"]))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            f'Overall Risk: <font color="{risk_hex}"><b>{overall}</b></font>',
            styles["Normal"]
        ))

        return story

    # ── Helpers ─────────────────────────────────────────────

    def _simple_table(self, rows, col_widths):
        t = Table(rows, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f0f0f0")),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
            ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("PADDING",    (0, 0), (-1, -1), 6),
        ]))
        return t

    def _overall_risk(self, summary) -> str:
        risk = summary.get("by_risk", {})
        for level in _RISK_PRIORITY:
            if risk.get(level, 0) > 0:
                return level
        return "NORMAL"

    def _assessment(self, evidence, summary) -> str:
        total   = summary["total_events"]
        overall = summary.get("overall_risk", "NORMAL")
        by_type = summary.get("by_type", {})

        if total == 0:
            return (
                "The candidate maintained normal behaviour throughout the entire session. "
                "No suspicious activity was detected."
            )

        intro = {
            "LOW":      "The candidate generally maintained normal behaviour with minor observations noted.",
            "MEDIUM":   "The candidate showed some suspicious behaviour patterns that require review.",
            "HIGH":     "The candidate exhibited several high-risk behaviours during the session.",
            "CRITICAL": "The candidate exhibited critical violations during the session requiring immediate attention.",
        }.get(overall, "Behaviour analysis complete.")

        parts = [intro]

        if "PHONE_WHILE_LOOKING_DOWN" in by_type:
            n = by_type["PHONE_WHILE_LOOKING_DOWN"]
            parts.append(
                f"{n} high-risk event(s) involving phone visibility while "
                f"looking downward were detected."
            )
        if "PHONE_VISIBLE" in by_type:
            parts.append(f"Phone visibility was flagged {by_type['PHONE_VISIBLE']} time(s).")
        if "LOOKING_AWAY" in by_type:
            parts.append(
                f"The candidate looked away beyond acceptable thresholds "
                f"{by_type['LOOKING_AWAY']} time(s)."
            )
        if "MULTIPLE_FACES" in by_type:
            parts.append(
                f"Multiple faces were detected simultaneously "
                f"{by_type['MULTIPLE_FACES']} time(s)."
            )
        if "NO_FACE" in by_type:
            parts.append(f"The candidate left the camera frame {by_type['NO_FACE']} time(s).")

        return " ".join(parts)
