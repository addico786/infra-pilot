import os
import smtplib
import html
from email.message import EmailMessage
from email.utils import parseaddr
from typing import Optional


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def email_enabled() -> bool:
    return _env_bool("EMAIL_ENABLED", default=False)


def _is_valid_email(value: str) -> bool:
    _, addr = parseaddr(value)
    if not addr or "@" not in addr:
        return False
    if any(ch.isspace() for ch in addr):
        return False
    return True


def send_analysis_email(*, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> None:
    """
    Best-effort SMTP email sender.

    This function is intentionally synchronous and should be called from a background task.
    It raises on misconfiguration or send failures so the caller can log the error.
    """
    if not _is_valid_email(to_email):
        raise ValueError("Invalid recipient email address")

    host = os.getenv("SMTP_HOST", "").strip()
    port_raw = os.getenv("SMTP_PORT", "").strip() or "587"
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    from_email = (os.getenv("EMAIL_FROM") or username).strip()

    if not host:
        raise RuntimeError("SMTP_HOST is not set")
    if not from_email or not _is_valid_email(from_email):
        raise RuntimeError("EMAIL_FROM is not set (or invalid)")
    if not username:
        raise RuntimeError("SMTP_USERNAME is not set")
    if not password:
        raise RuntimeError("SMTP_PASSWORD is not set")

    try:
        port = int(port_raw)
    except ValueError as e:
        raise RuntimeError("SMTP_PORT must be an integer") from e

    use_tls = _env_bool("SMTP_USE_TLS", default=True)

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    if html_body:
        msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(host=host, port=port, timeout=15) as smtp:
        smtp.ehlo()
        if use_tls:
            smtp.starttls()
            smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(msg)


def build_analysis_email_body(
    *,
    drift_score: float,
    provider: Optional[str],
    model: Optional[str],
    issues: list,
    timeline: list,
    max_issues: int = 8,
) -> str:
    provider_part = provider or "unknown"
    model_part = model or "default"
    drift_percentage = round(max(0.0, min(1.0, drift_score)) * 100)
    lines: list[str] = []
    lines.append("InfraPilot analysis results")
    lines.append("")
    lines.append(f"Drift score: {drift_percentage}%")
    lines.append(f"Provider/model: {provider_part} / {model_part}")
    lines.append("")

    lines.append(f"Issues ({len(issues)}):")
    if not issues:
        lines.append("- None")
    else:
        for issue in issues[:max_issues]:
            title = getattr(issue, "title", None) or str(getattr(issue, "id", "Issue"))
            severity = getattr(issue, "severity", None) or "unknown"
            resource = getattr(issue, "resource", None) or "unknown"
            lines.append(f"- [{severity}] {title} ({resource})")
        if len(issues) > max_issues:
            lines.append(f"- ... and {len(issues) - max_issues} more")

    lines.append("")
    lines.append(f"Timeline ({len(timeline)}):")
    if not timeline:
        lines.append("- None")
    else:
        for event in timeline[:8]:
            day = getattr(event, "day", 0)
            ev = getattr(event, "event", "") or ""
            sev = getattr(event, "severity", "info")
            lines.append(f"- Day {day}: [{sev}] {ev}")

    lines.append("")
    lines.append("Note: This email is best-effort. If you did not request it, you can ignore it.")
    return "\n".join(lines)


def _severity_color(severity: str) -> str:
    sev = (severity or "").lower()
    if sev == "critical":
        return "#dc2626"
    if sev == "high":
        return "#ea580c"
    if sev == "medium":
        return "#ca8a04"
    if sev == "low":
        return "#2563eb"
    return "#64748b"


def build_analysis_email_html(
    *,
    drift_score: float,
    provider: Optional[str],
    model: Optional[str],
    issues: list,
    timeline: list,
    max_issues: int = 8,
) -> str:
    provider_part = html.escape(provider or "unknown")
    model_part = html.escape(model or "default")
    drift_percentage = round(max(0.0, min(1.0, drift_score)) * 100)

    issue_items: list[str] = []
    for issue in issues[:max_issues]:
        title = html.escape(getattr(issue, "title", None) or str(getattr(issue, "id", "Issue")))
        severity = (getattr(issue, "severity", None) or "unknown").lower()
        resource = html.escape(getattr(issue, "resource", None) or "unknown")
        issue_items.append(
            f"""
            <div style="border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px;margin-bottom:10px;background:#ffffff;">
              <div style="font-size:14px;font-weight:700;color:#0f172a;margin-bottom:6px;">{title}</div>
              <div style="font-size:12px;color:#475569;">
                <span style="display:inline-block;padding:2px 8px;border-radius:999px;background:{_severity_color(severity)};color:#ffffff;margin-right:8px;text-transform:uppercase;font-weight:700;letter-spacing:.3px;">{html.escape(severity)}</span>
                Resource: {resource}
              </div>
            </div>
            """
        )
    if not issue_items:
        issue_items.append('<div style="font-size:13px;color:#475569;">No issues detected.</div>')
    if len(issues) > max_issues:
        issue_items.append(
            f'<div style="font-size:12px;color:#64748b;">... and {len(issues) - max_issues} more issue(s)</div>'
        )

    timeline_items: list[str] = []
    for event in timeline[:8]:
        day = getattr(event, "day", 0)
        ev = html.escape(getattr(event, "event", "") or "")
        sev = (getattr(event, "severity", "info") or "info").lower()
        timeline_items.append(
            f"""
            <tr>
              <td style="padding:8px 0;font-size:12px;color:#334155;white-space:nowrap;width:70px;">Day {day}</td>
              <td style="padding:8px 10px;">
                <span style="display:inline-block;padding:2px 8px;border-radius:999px;background:{_severity_color(sev)};color:#ffffff;font-size:11px;font-weight:700;margin-right:8px;text-transform:uppercase;">{html.escape(sev)}</span>
                <span style="font-size:13px;color:#0f172a;">{ev}</span>
              </td>
            </tr>
            """
        )
    if not timeline_items:
        timeline_items.append(
            '<tr><td colspan="2" style="padding:8px 0;font-size:13px;color:#475569;">No timeline events.</td></tr>'
        )

    return f"""<!doctype html>
<html>
  <body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:24px 12px;">
      <tr>
        <td align="center">
          <table role="presentation" width="680" cellpadding="0" cellspacing="0" style="max-width:680px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e2e8f0;">
            <tr>
              <td style="background:linear-gradient(135deg,#0f172a,#1d4ed8);padding:20px 24px;color:#ffffff;">
                <div style="font-size:18px;font-weight:700;">InfraPilot Analysis Results</div>
                <div style="font-size:12px;opacity:.9;margin-top:4px;">Automated infrastructure drift summary</div>
              </td>
            </tr>
            <tr>
              <td style="padding:18px 24px;">
                <div style="display:inline-block;background:#eff6ff;color:#1d4ed8;border:1px solid #bfdbfe;padding:8px 12px;border-radius:10px;font-size:13px;font-weight:700;">
                  Drift Score: {drift_percentage}%
                </div>
                <div style="margin-top:10px;font-size:13px;color:#334155;">
                  Provider/Model: <strong>{provider_part} / {model_part}</strong>
                </div>
              </td>
            </tr>
            <tr>
              <td style="padding:0 24px 8px;">
                <div style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:10px;">Issues ({len(issues)})</div>
                {''.join(issue_items)}
              </td>
            </tr>
            <tr>
              <td style="padding:8px 24px 16px;">
                <div style="font-size:16px;font-weight:700;color:#0f172a;margin-bottom:8px;">Timeline ({len(timeline)})</div>
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #e2e8f0;">
                  {''.join(timeline_items)}
                </table>
              </td>
            </tr>
            <tr>
              <td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:12px 24px;font-size:11px;color:#64748b;">
                This is a best-effort notification from InfraPilot. If you did not request this email, you can ignore it.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""

