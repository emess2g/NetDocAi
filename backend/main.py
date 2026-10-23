from pathlib import Path
import logging
import os
from fastapi import Depends
from auth import get_current_user

from fastapi import (
    FastAPI,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from parsers.interfaces import parse_interfaces
from parsers.vlans import parse_vlans
from parsers.routing import parse_ospf, parse_ospf_processes
from parsers.routing import parse_eigrp, parse_eigrp_processes
from parsers.routing import parse_static_routes
from parsers.routing import parse_bgp
from parsers.stp import parse_stp
from parsers.security import parse_security
from parsers.acl import parse_acls
from analyzers.acl_analyzer import analyze_acls
from parsers.hostname import parse_hostname
from parsers.syslog import looks_like_syslog, parse_syslog
from parsers.snmp import parse_snmp
from analyzers.syslog_analyzer import analyze_syslog_events
from analyzers.snmp_analyzer import analyze_snmp
from parsers.dhcp import parse_dhcp
from analyzers.dhcp_analyzer import analyze_dhcp
from analyzers.cross_feature_analyzer import (
    analyze_dhcp_interface_consistency,
    analyze_nat_interface_consistency,
    analyze_dhcp_gateway_interface_consistency,
)
from parsers.nat import parse_nat
from parsers.cdp import parse_cdp
from core.network_model import build_network_model
from core.network_model_validation import validate_network_model

from analyzers.interface_analyzer import analyze_interfaces
from analyzers.vlan_analyzer import analyze_vlans
from analyzers.routing_analyzer import (
    analyze_routing,
    analyze_ospf_processes,
    analyze_eigrp_processes,
)
from analyzers.stp_analyzer import analyze_stp
from analyzers.security_analyzer import analyze_security
from analyzers.nat_analyzer import analyze_nat
from analyzers.cdp_analyzer import analyze_cdp

from core.health import calculate_health_score
from core.summary import calculate_summary


app = FastAPI(title="NetDoc AI")
MAX_CONFIG_SIZE = 1_000_000
ALLOWED_CONFIG_EXTENSIONS = {".cfg", ".conf", ".txt", ".log"}

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://net-doc-ai.vercel.app",
    "https://net-doc-kq3dwutjs-emess2gs-projects.vercel.app",
]

CORS_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv(
        "CORS_ORIGINS",
        ",".join(DEFAULT_CORS_ORIGINS),
    ).split(",")
    if origin.strip()
]

logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigRequest(BaseModel):
    config: str = Field(
        min_length=1,
        max_length=1_000_000,
    )

    @field_validator("config")
    @classmethod
    def validate_config(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Configuration cannot be empty")

        if "\x00" in value:
            raise ValueError("Configuration contains a NUL character")

        return value


@app.get("/")
def home():
    return {
        "message": "NetDoc AI",
        "status": "backend running",
    }

@app.post("/analyze")
def analyze(
    request: ConfigRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        return analyze_config(request.config)
    except Exception:
        logger.exception("Unexpected error while analyzing network configuration")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the configuration.",
        ) from None

def calculate_syslog_event_risk(findings: list[dict]) -> dict:
    """Score supplied Syslog finding severities, not live network health."""
    points = {"critical": 25, "high": 12, "warning": 4, "info": 0}
    score = max(
        0,
        100 - sum(points.get(str(item.get("severity", "")).lower(), 0) for item in findings),
    )

    if score >= 90:
        status = "Low event risk"
    elif score >= 75:
        status = "Moderate event risk"
    elif score >= 50:
        status = "Elevated event risk"
    else:
        status = "High event risk"

    return {
        "score": score,
        "status": status,
        "basis": "Heuristic score from supplied Syslog finding severities; not live network health.",
    }

def analyze_config(config: str):
    # Syslog is event data rather than running configuration. Detect it before
    # invoking configuration parsers so log lines become useful findings.
    if looks_like_syslog(config):
        events = parse_syslog(config)
        findings = analyze_syslog_events(events)
        devices = sorted({event["device"] for event in events})
        hostname = devices[0] if len(devices) == 1 else "Syslog Analysis"
        # Syslog is not a running configuration assessment; return a separate
        # event-risk score based on the severities of the supplied findings.
        health = calculate_syslog_event_risk(findings)
        summary = {
            "total_findings": len(findings),
            "critical": sum(item["severity"] == "critical" for item in findings),
            "high": sum(item["severity"] == "high" for item in findings),
            "warning": sum(item["severity"] == "warning" for item in findings),
            "info": sum(item["severity"] == "info" for item in findings),
            "devices": len(devices),
            "events": len(events),
            "overview": (
                f"Parsed {len(events)} Syslog events across {len(devices)} device(s). "
                f"{sum(item['severity'] in {'critical', 'high'} for item in findings)} "
                "high-priority event(s) need review."
            ),
        }
        return {
            "report_type": "syslog",
            "hostname": hostname,
            "interfaces": [],
            "vlans": [],
            "ospf": None,
            "eigrp": None,
            "static_routes": [],
            "bgp": None,
            "stp": {},
            "security": {},
            "acls": [],
            "dhcp": {},
            "nat": {},
            "cdp": {},
            "snmp": {},
            "syslog_events": events,
            "findings": findings,
            "health": health,
            "summary": summary,
        }

    hostname = parse_hostname(config)

    interfaces = parse_interfaces(config)
    vlans = parse_vlans(config)

    ospf_processes = parse_ospf_processes(config)
    ospf = ospf_processes[0] if ospf_processes else None
    eigrp_processes = parse_eigrp_processes(config)
    eigrp = eigrp_processes[0] if eigrp_processes else None
    static_routes = parse_static_routes(config)
    bgp = parse_bgp(config)

    stp = parse_stp(config)
    security = parse_security(config)
    acls = parse_acls(config)
    dhcp = parse_dhcp(config)
    nat = parse_nat(config)
    cdp = parse_cdp(config)
    snmp = parse_snmp(config)
    interface_findings = analyze_interfaces(interfaces)
    vlan_findings = analyze_vlans(vlans, interfaces)


    cross_feature_findings = analyze_dhcp_interface_consistency(
        dhcp,
        interfaces,
    )

    cross_feature_findings.extend(
        analyze_dhcp_gateway_interface_consistency(
            dhcp,
            interfaces,
        )
    )

    cross_feature_findings.extend(
        analyze_nat_interface_consistency(nat, interfaces)
    )


    routing_findings = analyze_routing(
        None, None, static_routes, bgp
    )

    routing_findings.extend(
        analyze_ospf_processes(ospf_processes)
    )

    routing_findings.extend(
        analyze_eigrp_processes(eigrp_processes)
    )

    stp_findings = analyze_stp(stp)
    security_findings = analyze_security(security)
    acl_findings = analyze_acls(acls)
    dhcp_findings = analyze_dhcp(dhcp)
    nat_findings = analyze_nat(nat)
    cdp_findings = analyze_cdp(cdp)
    snmp_findings = analyze_snmp(snmp)

    findings = (
        interface_findings
        + vlan_findings
        + routing_findings
        + stp_findings
        + security_findings
        + acl_findings
        + dhcp_findings
        + nat_findings
        + cdp_findings
        + snmp_findings
        + cross_feature_findings
    )

    network_model = build_network_model(
        hostname=hostname,
        interfaces=interfaces,
        vlans=vlans,
        dhcp=dhcp,
        cdp=cdp,
    )

    network_model_errors = validate_network_model(network_model)
    network_model_validation = {
        "valid": not network_model_errors,
        "errors": network_model_errors,
    }

    health = calculate_health_score(findings)
    summary = calculate_summary(
        findings,
        hostname=hostname,
        interfaces=interfaces,
        vlans=vlans,
        ospf=ospf,
        eigrp=eigrp,
        static_routes=static_routes,
        bgp=bgp,
        security=security,
        dhcp=dhcp,
        nat=nat,
        cdp=cdp,
        acls=acls
    )

    return {
        "hostname": hostname,
        "interfaces": interfaces,
        "vlans": vlans,
        "ospf": ospf,
        "eigrp": eigrp,
        "static_routes": static_routes,
        "bgp": bgp,
        "stp": stp,
        "security": security,
        "acls": acls,
        "dhcp": dhcp,
        "nat": nat,
        "cdp": cdp,
        "snmp": snmp,
        "findings": findings,
        "health": health,
        "summary": summary,
        "ospf_processes": ospf_processes,
        "eigrp_processes": eigrp_processes,
        "network_model": network_model,
        "network_model_validation": network_model_validation,
    }


@app.post("/analyze/upload")
async def analyze_upload(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        filename = file.filename or ""
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_CONFIG_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported file type. "
                    "Upload a .cfg, .conf, .txt, or .log file."
                ),
            )

        content = await file.read(MAX_CONFIG_SIZE + 1)

        if len(content) > MAX_CONFIG_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Configuration file exceeds the 1 MB limit.",
            )

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Configuration file is empty.",
            )

        try:
            config = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Configuration file must use UTF-8 encoding.",
            )

        if not config.strip():
            raise HTTPException(
                status_code=400,
                detail="Configuration file cannot contain only whitespace.",
            )

        if "\x00" in config:
            raise HTTPException(
                status_code=400,
                detail="Configuration file contains a NUL character.",
            )

    finally:
        await file.close()

    try:
        return analyze_config(config)
    except Exception:
        logger.exception("Unexpected error while analyzing uploaded configuration")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the configuration.",
        ) from None
