from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_detects_dhcp_interface_subnet_mismatch():
    config = """
hostname R1

interface GigabitEthernet0/0
 description LAN interface
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!

ip dhcp pool USERS
 network 10.10.10.0 255.255.255.0
 default-router 10.10.10.1
 dns-server 8.8.8.8
!
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    cross_feature_findings = [
        finding
        for finding in data["findings"]
        if finding.get("category") == "cross_feature"
    ]

    assert len(cross_feature_findings) == 1

    finding = cross_feature_findings[0]

    assert finding["severity"] == "warning"
    assert "10.10.10.0/24" in finding["finding"]
    assert "192.168.1.0/24" in str(finding["evidence"])


def test_analyze_detects_nat_reference_to_missing_interface():
    config = """
hostname R1

interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 ip nat inside
 no shutdown
!

interface GigabitEthernet0/1
 ip address 203.0.113.2 255.255.255.0
 ip nat outside
 no shutdown
!

ip nat inside source list 1 interface GigabitEthernet0/2 overload
"""

    response = client.post("/analyze", json={"config": config})

    assert response.status_code == 200

    data = response.json()

    nat_cross_feature_findings = [
        finding
        for finding in data["findings"]
        if finding.get("category") == "cross_feature"
        and "GigabitEthernet0/2" in finding.get("finding", "")
    ]

    assert len(nat_cross_feature_findings) == 1
    assert nat_cross_feature_findings[0]["severity"] == "warning"
