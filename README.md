# Awesome MedTech Requirements [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

A curated list of tools, standards, and research projects to help medtech teams manage requirements and risk in compliance with [IEC 62304](https://www.iso.org/standard/38421.html), [ISO 14971](https://www.iso.org/standard/72704.html), and [ISO 13485](https://www.iso.org/standard/59752.html) (as well as FDA design controls).

> [!TIP]
> This list is new, and is not exhaustive. Contributions are welcome!

## Key

| Symbol | Meaning |
|--------|---------|
| 🆓 | Open Source (or Free to Use) |
| 💰 | Commercial/Paid |

## Contents
- [Requirements Management Tools (standalone)](#requirements-management-tools-standalone)
- [Requirements Management Tools (in Jira)](#requirements-management-tools-in-jira)
- [Requirements Management Tools (embedded in other tools)](#requirements-management-tools-embedded-in-other-tools)
- [Requirements Management Tools (within eQMS)](#requirements-management-tools-within-eqms)
- [Interchange Standards](#interchange-standards)
- [Academic Projects & Research](#academic-projects--research)
- [Templates](#templates)

## Requirements Management Tools (standalone)

- **[Doorstop](https://doorstop.readthedocs.io/)**
  An open source requirements management tool that leverages Git for version control. 🆓
- **[OSRMT](https://github.com/osrmt/osrmt)**
  A free tool for full SDLC traceability of features, requirements, design, and tests. 🆓
- **[rmtoo](https://github.com/florath/rmtoo)**
  Command-line requirements management via text files and version control. 🆓
- **[Eclipse RMF / ReqIF Studio](https://www.eclipse.org/rmf/)**
  An open implementation of the ReqIF standard for requirements exchange. 🆓
- **[Sphinx-Needs](https://www.sphinx-needs.com/)**
  A documentation tool for managing and presenting requirements 🆓
- **[StrictDoc](https://strictdoc.readthedocs.io/)**
  A documentation and requirements management tool with focus on traceability, custom fields, and source code linking. Supports export to HTML, RST, ReqIF, PDF, JSON, and Excel. 🆓
- **[ReqView](https://www.reqview.com/)**
  A lightweight requirements management tool with Git integration, suitable for medical device compliance with full traceability and customizable templates. 💰
- **[IBM Engineering DOORS/DOORS Next](https://www.ibm.com/products/engineering-doors)**
  Widely used in regulated environments, offering robust traceability and compliance support. Frankly better suited for large organizations. 💰
- **[Matrix ALM](https://matrixreq.com/products/alm)**
  Designed for medtech, offering comprehensive traceability between requirements, risks, and tests. 💰
- **[Jama Connect](https://www.jamasoftware.com/platform/jama-connect/)**
  A modern platform offering end-to-end traceability and review workflows. 💰
- **[Siemens Polarion ALM](https://www.plm.automation.siemens.com/global/en/products/polarion/)**
  Features a dedicated MedPack template for IEC 62304 compliance. 💰
- **[PTC Codebeamer ALM](https://www.ptc.com/en/products/codebeamer)**
  Provides pre-configured medical process templates and dynamic traceability. 💰
- **[Visure Requirements](https://www.visuresolutions.com/)**
  An ALM solution with traceability across requirements, risks, and tests. 💰
- **[Cognition Cockpit/Compass](https://cognition.us/solutions/compass-med/)**
  A tailored platform for risk management with integrated hazard analysis and traceability. 💰
- **[Perforce Helix ALM](https://www.perforce.com/products/helix-alm)**
  Integrates requirements, test, and issue management for compliance. 💰
- **[Visure Requirements](https://www.visuresolutions.com/)**
  Generates comprehensive traceability reports aligned with IEC 62304. 💰
- **[Tento plus](https://tentoplus.com/)**
  A requirements management tool with AI, suitable for medical device compliance with full traceability. 💰

## Requirements Management Tools (in Jira)

Resources for setting up your Requirements and Risk Management in [Jira](https://www.atlassian.com/software/jira):

- **[SoftComply Risk Manager (for Jira)](https://softcomply.com/)**
  A Jira plugin that transforms Jira into a risk tracker for ISO 14971. 💰
- **[Capable Risk for Jira](https://marketplace.atlassian.com/apps/1236515/capable-risk-for-jira)**
  A Jira plugin that adds support for risk management and traceability for ISO 14971, as well as CVSS for security risk assessment. 💰
- **[Snapshots for Jira](https://marketplace.atlassian.com/apps/1225123/snapshots-of-jira-data-into-confluence)**
  A confluence/jira plugin for creating point-in-time snapshots of Jira data, such as requirements traces, as well as risk management. 💰
- **[Ketryx](https://www.ketryx.com/)**
  A Jira integrated tool which extends Jira with requirements management and risk management features, SBOM, security features, and more - everything needed to setup a medtech compliance workflow and agile delivery system. 💰

## Requirements Management Tools (embedded in other tools)

- **[Modern Requirements](https://www.modernrequirements.com/)**
  An Azure DevOps integrated tool for streamlined requirements management. 💰

## Requirements Management Tools (within eQMS)

Includes eQMS tools whcih have a requirements management function suitable for medtech.

- **[Greenlight Guru](https://www.greenlight.guru/)**
  An eQMS solution featuring a dedicated requirements and risk management module for ISO 62304/14971/13485. 💰
- **[Dot Compliance](https://www.dotcompliance.com/)**
  An eQMS solution featuring a dedicated requirements and risk management module for ISO 62304/14971/13485. 💰
- **[Qualio](https://www.qualio.com/)**
  An eQMS solution featuring a dedicated requirements and risk management module for ISO 62304/14971/13485. 💰
- **[Open Regulatory Formwork](https://openregulatory.org/)**
  An eQMS solution featuring a dedicated requirements and risk management module for ISO 62304/14971/13485. 💰

## Interchange Standards

- **[ReqIF](https://www.omg.org/spec/ReqIF/)**
  The OMG standard XML schema for exchanging requirements between tools. 🆓
- **[SpecIF](http://specif.de/)**
  An emerging vendor-neutral standard building on ReqIF concepts. 🆓
- **[OSLC](https://open-services.net/)**
  Defines RESTful web service interfaces for real-time sharing of requirements data. 🆓

## Academic Projects & Research

- **[OpenReq Project](https://openreq.eu/)**
  An EU H2020 initiative offering intelligent recommendations for requirements management.
- **[MDevSPICE Framework](https://link.springer.com/chapter/10.1007/978-3-319-13036-1_26)**
  A consolidated process model integrating IEC 62304, ISO 14971, ISO 13485, and FDA controls.
- **[Multi-level Requirements Modelling Research](https://scholar.google.com/scholar?q=Multi-level+Requirements+Modelling+MedTech)**
  Research on decomposing and tracing user needs through to software requirements.
- **[Standards Evolution and Trace Research](https://scholar.google.com/scholar?q=standards+evolution+trace+requirements+medtech)**
  Studies on adapting requirements management tools to evolving standards.

## Templates

n.b. that most/all paid QMS tools provide templates.

- **[OpenRegulatory Templates](https://openregulatory.org/)**
  Community-driven open templates covering IEC 62304, ISO 14971, and ISO 13485. 🆓

Contributions, improvements, and corrections are always welcome! Please use github issues and/or pull requests to contribute.
