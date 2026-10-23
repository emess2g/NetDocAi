import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

const COLORS = {
  navy: [15, 23, 42],
  blue: [37, 99, 235],
  muted: [100, 116, 139],
  light: [241, 245, 249],
  white: [255, 255, 255],
};

function safeText(value, fallback = "—") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }

  if (Array.isArray(value)) {
    return value.map((item) => safeText(item)).join(", ");
  }

  if (typeof value === "object") {
    return Object.entries(value)
      .map(([key, item]) => `${key}: ${safeText(item)}`)
      .join("; ");
  }

  return String(value);
}

function getHealth(network) {
  if (network.health && typeof network.health === "object") {
    return network.health.score ?? network.health_score ?? null;
  }

  return network.health_score ?? network.health ?? null;
}

function getStatus(network) {
  if (network.health && typeof network.health === "object") {
    return network.health.status ?? network.health_status ?? "Not available";
  }

  return network.health_status ?? "Not available";
}

function getSeverity(finding) {
  return safeText(finding?.severity, "Unspecified").toUpperCase();
}

function getFindingTitle(finding, isSyslogReport) {
  if (isSyslogReport) {
    return safeText(
      finding.finding ?? finding.title ?? finding.name ?? finding.event_code,
      "Syslog event",
    );
  }

  return safeText(
    finding.title ?? finding.name ?? finding.rule ?? finding.type,
    "Network finding",
  );
}

function getFindingDetails(finding, isSyslogReport) {
  if (isSyslogReport) {
    return [
      `Device: ${safeText(finding.device)}`,
      `Time: ${safeText(finding.timestamp)}`,
      `Event: ${safeText(finding.event_code)}`,
      `Details: ${safeText(finding.impact ?? finding.message)}`,
      `Recommendation: ${safeText(finding.recommendation)}`,
    ].join("\\n");
  }

  return safeText(
    finding.description ??
      finding.recommendation ??
      finding.message ??
      finding.details,
  );
}

function sectionTitle(doc, title, y) {
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.setTextColor(...COLORS.navy);
  doc.text(title, 14, y);

  doc.setDrawColor(...COLORS.blue);
  doc.setLineWidth(0.6);
  doc.line(14, y + 2, 196, y + 2);

  return y + 8;
}

function addTable(doc, options) {
  autoTable(doc, {
    theme: "striped",
    margin: { left: 14, right: 14, top: 18, bottom: 20 },
    styles: {
      font: "helvetica",
      fontSize: 8,
      cellPadding: 3,
      overflow: "linebreak",
      valign: "top",
      textColor: COLORS.navy,
      lineColor: [226, 232, 240],
      lineWidth: 0.1,
    },
    headStyles: {
      fillColor: COLORS.navy,
      textColor: COLORS.white,
      fontStyle: "bold",
    },
    alternateRowStyles: {
      fillColor: [248, 250, 252],
    },
    ...options,
  });
}

function addPageFooters(doc) {
  const pageCount = doc.getNumberOfPages();

  for (let page = 1; page <= pageCount; page += 1) {
    doc.setPage(page);

    const pageHeight = doc.internal.pageSize.getHeight();

    doc.setDrawColor(226, 232, 240);
    doc.line(14, pageHeight - 14, 196, pageHeight - 14);

    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(...COLORS.muted);

    doc.text("NetDocAi | Confidential technical report", 14, pageHeight - 8);
    doc.text(`Page ${page} of ${pageCount}`, 196, pageHeight - 8, {
      align: "right",
    });
  }
}

export function exportNetworkReport(network, metadata = {}) {
  if (!network || typeof network !== "object") {
    throw new Error("No valid network analysis is available to export.");
  }

  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const isSyslogReport = network.report_type === "syslog";
  const reportType = isSyslogReport
    ? "SYSLOG EVENT ANALYSIS"
    : "NETWORK CONFIGURATION ANALYSIS";

  const hostname = safeText(
    metadata.hostname ?? network.hostname,
    "Unknown Device",
  );

  const createdAt = metadata.createdAt
    ? new Date(metadata.createdAt)
    : new Date();

  const dateText = Number.isNaN(createdAt.getTime())
    ? "Not available"
    : createdAt.toLocaleString();

  const findings = Array.isArray(network.findings) ? network.findings : [];

  const interfaces = Array.isArray(network.interfaces)
    ? network.interfaces
    : [];

  const vlans = Array.isArray(network.vlans) ? network.vlans : [];

  const health = getHealth(network);
  const status = getStatus(network);

  const countSeverity = (severity) =>
    findings.filter(
      (finding) => String(finding?.severity || "").toLowerCase() === severity,
    ).length;

  // Cover / executive summary
  doc.setFillColor(...COLORS.navy);
  doc.rect(0, 0, 210, 53, "F");

  doc.setTextColor(...COLORS.white);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(23);
  doc.text("NetDocAi", 14, 19);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.text(reportType, 14, 28);

  doc.setFontSize(17);
  doc.text("Technical Report", 14, 42);

  doc.setTextColor(...COLORS.navy);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text(hostname, 14, 68);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(...COLORS.muted);
  doc.text(`Report generated: ${dateText}`, 14, 76);

  // Summary metric cards
  const syslogEvents = Array.isArray(network.syslog_events)
    ? network.syslog_events
    : [];

  const metrics = [
    { label: isSyslogReport ? "EVENT RISK SCORE" : "HEALTH SCORE", value: health ?? "N/A" },
    { label: isSyslogReport ? "TOTAL EVENTS" : "TOTAL FINDINGS", value: isSyslogReport ? syslogEvents.length : findings.length },
    { label: isSyslogReport ? "DEVICES" : "INTERFACES", value: isSyslogReport ? new Set(syslogEvents.map((event) => event.device)).size : interfaces.length },
    { label: isSyslogReport ? "HIGH FINDINGS" : "VLANS", value: isSyslogReport ? findings.filter((finding) => String(finding?.severity || "").toLowerCase() === "high").length : vlans.length },
  ];

  const cardY = 87;
  const cardW = 43.5;
  const cardGap = 3;

  metrics.forEach((metric, index) => {
    const x = 14 + index * (cardW + cardGap);

    doc.setFillColor(...COLORS.light);
    doc.roundedRect(x, cardY, cardW, 23, 2, 2, "F");

    doc.setFont("helvetica", "normal");
    doc.setFontSize(7);
    doc.setTextColor(...COLORS.muted);
    doc.text(metric.label, x + 3, cardY + 7);

    doc.setFont("helvetica", "bold");
    doc.setFontSize(15);
    doc.setTextColor(...COLORS.navy);
    doc.text(String(metric.value), x + 3, cardY + 17);
  });

  let y = sectionTitle(doc, "Executive Summary", 123);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(...COLORS.navy);

  const summaryText = [
    `Device / report: ${hostname}`,
    `${isSyslogReport ? "Event risk status" : "Overall status"}: ${safeText(status)}`,
    `Critical findings: ${countSeverity("critical")}`,
    `High findings: ${countSeverity("high")}`,
    ...(isSyslogReport
      ? [
          `Warnings: ${countSeverity("warning")}`,
          `Informational: ${countSeverity("info")}`,
        ]
      : [
          `Medium findings: ${countSeverity("medium")}`,
          `Low findings: ${countSeverity("low")}`,
        ]),
  ];

  summaryText.forEach((line) => {
    doc.text(line, 16, y);
    y += 6;
  });

  // Findings
  y += 5;
  y = sectionTitle(
    doc,
    isSyslogReport ? "Syslog Findings and Recommendations" : "Findings and Recommendations",
    y,
  );

  if (findings.length) {
    addTable(doc, {
      startY: y,
      head: [["Severity", "Finding", "Details / Recommendation"]],
      body: findings.map((finding) => [
        getSeverity(finding),
        getFindingTitle(finding, isSyslogReport),
        getFindingDetails(finding, isSyslogReport),
      ]),
      columnStyles: {
        0: { cellWidth: 25 },
        1: { cellWidth: 52 },
        2: { cellWidth: "auto" },
      },
    });
  } else {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text("No findings were returned by the analyzer.", 14, y + 3);
  }

  if (isSyslogReport) {
    doc.addPage();
    y = sectionTitle(doc, "Parsed Syslog Events", 20);

    if (syslogEvents.length) {
      addTable(doc, {
        startY: y,
        head: [["Timestamp", "Device", "Event Code", "Raw Message"]],
        body: syslogEvents.map((event) => [
          safeText(event.timestamp),
          safeText(event.device),
          safeText(`${event.facility}-${event.severity}-${event.mnemonic}`),
          safeText(event.raw ?? event.message),
        ]),
        columnStyles: {
          0: { cellWidth: 35 },
          1: { cellWidth: 27 },
          2: { cellWidth: 35 },
          3: { cellWidth: "auto" },
        },
      });
    } else {
      doc.text("No parsed Syslog events were returned.", 14, y + 3);
    }
  } else {
    // Configuration reports retain their interface, VLAN, routing, and service inventories.
    doc.addPage();
    y = sectionTitle(doc, "Interface Inventory", 20);

    if (interfaces.length) {
      addTable(doc, {
        startY: y,
        head: [["Interface", "IP Address", "Status", "Mode", "VLAN"]],
        body: interfaces.map((item) => [
          safeText(item.name ?? item.interface ?? item.interface_name),
          safeText(item.ip_address ?? item.ip),
          safeText(item.status),
          safeText(item.mode),
          safeText(item.access_vlan ?? item.vlan ?? item.allowed_vlans),
        ]),
      });
    } else {
      doc.text("No interface data available.", 14, y + 3);
    }

    y = (doc.lastAutoTable?.finalY ?? y) + 14;
    y = sectionTitle(doc, "VLAN Inventory", y);

    if (vlans.length) {
      addTable(doc, {
        startY: y,
        head: [["VLAN ID", "Name", "Status", "Additional Details"]],
        body: vlans.map((vlan) => {
          if (typeof vlan !== "object" || vlan === null) {
            return [safeText(vlan), "—", "—", "—"];
          }

          return [
            safeText(vlan.id ?? vlan.vlan_id ?? vlan.number),
            safeText(vlan.name),
            safeText(vlan.status),
            safeText(vlan.description),
          ];
        }),
      });
    } else {
      doc.text("No VLAN data available.", 14, y + 3);
    }

    doc.addPage();
    y = sectionTitle(doc, "Routing Configuration", 20);

    const routingSections = [
      ["OSPF", network.ospf],
      ["EIGRP", network.eigrp],
      ["BGP", network.bgp],
      ["Static Routes", network.static_routes],
      ["Routing Summary", network.routing],
    ];

    const routingRows = routingSections
      .filter(([, value]) =>
        Array.isArray(value) ? value.length > 0 : Boolean(value),
      )
      .map(([name, value]) => [name, safeText(value)]);

    if (routingRows.length) {
      addTable(doc, {
        startY: y,
        head: [["Routing Feature", "Configuration Summary"]],
        body: routingRows,
        columnStyles: {
          0: { cellWidth: 35 },
          1: { cellWidth: "auto" },
        },
      });
    } else {
      doc.text("No routing data available.", 14, y + 3);
    }

    y = (doc.lastAutoTable?.finalY ?? y) + 14;
    y = sectionTitle(doc, "Security and Services", y);

    const serviceSections = [
      ["Security", network.security],
      ["Access Control Lists", network.acls],
      ["DHCP", network.dhcp],
      ["NAT", network.nat],
      ["CDP", network.cdp],
      ["Spanning Tree", network.stp],
    ];

    const serviceRows = serviceSections
      .filter(([, value]) =>
        Array.isArray(value) ? value.length > 0 : Boolean(value),
      )
      .map(([name, value]) => [name, safeText(value)]);

    if (serviceRows.length) {
      addTable(doc, {
        startY: y,
        head: [["Feature", "Analysis Details"]],
        body: serviceRows,
        columnStyles: {
          0: { cellWidth: 35 },
          1: { cellWidth: "auto" },
        },
      });
    } else {
      doc.text("No additional service data available.", 14, y + 3);
    }
  }

  // Methodology note
  doc.addPage();
  y = sectionTitle(doc, "Report Notes", 20);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(...COLORS.navy);

  const notes = isSyslogReport
    ? [
        "This report summarizes Syslog events parsed from the supplied log input.",
        "Severity and recommendations are heuristic indicators; validate them against surrounding logs and live device state.",
        "A denied packet does not by itself prove malicious activity.",
        "Use timestamps, device names, event codes, and raw messages to correlate findings with the original logs.",
        "Treat this document as confidential if it contains sensitive infrastructure information.",
      ]
    : [
        "This report summarizes the configuration analysis returned by NetDocAi.",
        "Findings depend on the configuration text supplied and the analyzer's current rules.",
        "Validate recommendations against your network design and operational requirements before making changes.",
        "This report does not guarantee that the live network matches the supplied configuration.",
        "Treat this document as confidential if it contains sensitive infrastructure information.",
      ];

  notes.forEach((note) => {
    const lines = doc.splitTextToSize(`• ${note}`, 180);
    doc.text(lines, 14, y);
    y += lines.length * 5 + 4;
  });

  addPageFooters(doc);

  const safeHostname =
    hostname
      .replace(/[^a-z0-9_-]+/gi, "_")
      .replace(/^_+|_+$/g, "")
      .slice(0, 70) || "network";

  const dateStamp = createdAt.toISOString().slice(0, 10);

  doc.save(`NetDocAi_${safeHostname}_${dateStamp}.pdf`);
}
