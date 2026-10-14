from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
from parsers.dhcp import parse_dhcp
from analyzers.dhcp_analyzer import analyze_dhcp
from analyzers.cross_feature_analyzer import (
    analyze_dhcp_interface_consistency,
    analyze_nat_interface_consistency,
)
from parsers.nat import parse_nat
from parsers.cdp import parse_cdp

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConfigRequest(BaseModel):
    config: str


@app.get("/")
def home():
    return {
        "message": "NetDoc AI",
        "status": "backend running",
    }


@app.post("/analyze")
def analyze(request: ConfigRequest):
    hostname = parse_hostname(request.config)

    interfaces = parse_interfaces(request.config)
    vlans = parse_vlans(request.config)

    ospf_processes = parse_ospf_processes(request.config)
    ospf = ospf_processes[0] if ospf_processes else None
    eigrp_processes = parse_eigrp_processes(request.config)
    eigrp = eigrp_processes[0] if eigrp_processes else None
    static_routes = parse_static_routes(request.config)
    bgp = parse_bgp(request.config)

    stp = parse_stp(request.config)
    security = parse_security(request.config)
    acls = parse_acls(request.config)
    dhcp = parse_dhcp(request.config)
    nat = parse_nat(request.config)
    cdp = parse_cdp(request.config)
    interface_findings = analyze_interfaces(interfaces)
    vlan_findings = analyze_vlans(vlans, interfaces)
    dhcp_findings = analyze_dhcp(dhcp)

    cross_feature_findings = analyze_dhcp_interface_consistency(
        dhcp,
        interfaces,
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
        + cross_feature_findings
    )

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
        "findings": findings,
        "health": health,
        "summary": summary,
        "ospf_processes": ospf_processes,
        "eigrp_processes": eigrp_processes,

    }
