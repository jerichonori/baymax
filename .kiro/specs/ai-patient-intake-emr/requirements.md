# Requirements Document - AI Intake + Lightweight EMR (India MVP)

## Introduction

This system provides an AI-powered patient intake and Electronic Medical Records (EMR) platform specifically designed for the Indian healthcare market. The system enables multilingual conversational patient interviews using AI to gather comprehensive medical information before appointments, with initial focus on orthopedics specialty. The system maintains strict compliance with Indian healthcare regulations (DPDPA 2023, Telemedicine Guidelines 2020) and never provides diagnoses to patients. All collected information is structured and presented to doctors in English through a lightweight EMR interface to support clinical decision-making.

## Product Vision

Reduce clinician administrative burden by 50% while increasing data completeness and patient safety via an AI-led intake that never diagnoses to patients and a lightweight EMR for rapid review and action.

## India MVP Decisions (Locked)

- **Geography & Compliance:** India (DPDPA 2023; NMC/MoHFW Telemedicine Guidelines 2020)
- **Data Hosting:** AWS India (ap-south-1/2)
- **Channels:** Web chat + Web voice (browser mic/WebRTC)
- **Languages:** AI understands multiple Indian languages; doctor output always English
- **Specialty (MVP):** Orthopedics
- **Virtual Visits:** Zoom (link generated on booking)
- **Identity Proofing:** OTP (SMS/email magic link)
- **Payments/Eligibility:** Out of scope (MVP)
- **Attachments:** Enabled (≤15 MB, ≤10 files, images+PDF only)
- **Staff Workflow:** None—intake delivers straight to the doctor
- **Training/Data Use:** Allowed—de-identified and tenant-opt-out supported
- **Brand/Tone:** Reassuring, clinical, concise
- **Mobile Offline:** Not required
- **Access Model:** Single brand (no per-clinic branding)

## Requirements

### Requirement 1 - Scheduling & Onboarding

**User Story:** As a patient, I want to book appointments and begin intake so that I can receive medical care efficiently.

#### Acceptance Criteria

1. WHEN a patient accesses the scheduling system THEN the system SHALL show real-time slots per doctor/location and confirm mode (Physical/Zoom)
2. WHEN a patient confirms an appointment THEN the system SHALL send confirmation + calendar invite + secure intake link (OTP/magic link)
3. WHEN a patient starts intake THEN the system SHALL allow save & resume with reminder nudges at +2h and +24h for abandoned sessions
4. WHEN virtual appointments are booked THEN the system SHALL generate Zoom links server-side and never expose them in public logs

### Requirement 2 - Identity, Consent & Safety Gate (India)

**User Story:** As a patient, I want to authenticate and consent before sharing PHI so that my data is protected according to Indian regulations.

#### Acceptance Criteria

1. WHEN a patient accesses intake THEN the system SHALL verify via OTP (phone/email) and merge duplicates by phone+DoB with clinician override
2. WHEN starting intake THEN the system SHALL capture explicit consent for AI-assisted intake and audio recording (voice)
3. WHEN the intake begins THEN the system SHALL display telemedicine banner: "AI does not diagnose; an RMP will review and advise"
4. WHEN patients interact THEN the system SHALL provide language picker and accessibility features (captions, WCAG AA)
5. IF patients provide ABHA number THEN the system SHALL store as patient identifier with consent string (ABDM model)
### Requirement 3 - Conversational Intake (Multilingual, English Output)

**User Story:** As a patient, I want to complete a guided interview in my preferred language so that I can provide comprehensive information naturally.

#### Acceptance Criteria

1. WHEN conducting intake THEN the system SHALL support web chat + web voice with seamless switching mid-flow without data loss
2. WHEN patients communicate THEN the system SHALL understand multilingual input (Indic + code-switching) and provide English summaries to doctors
3. WHEN gathering information THEN the system SHALL use structured frameworks: Ortho HPI (MOI, onset, weight-bearing, pain scale, swelling, deformity, ROM, neurovascular status), PMH, Meds, Allergies, ROS
4. IF patients ask for diagnosis THEN the system SHALL NOT provide diagnosis/Rx/prognosis and SHALL redirect to info-gathering or emergency guidance
5. WHEN intake is complete THEN the system SHALL use specialty-specific completeness score OR max turns OR patient stop as end conditions
6. IF red flags are detected THEN the system SHALL show emergency copy to patient + immediately page assigned doctor + log event
7. WHEN conversation ends THEN the system SHALL generate Structured Intake Bundle + plain-English summary including detected languages and confidence

### Requirement 4 - Orthopedics Playbook (MVP Specialty)

**User Story:** As an admin, I want orthopedics-specific questioning and safety protocols so that the system can handle bone and joint conditions appropriately.

#### Acceptance Criteria

1. WHEN configuring ortho flows THEN the system SHALL provide question banks for adult & pediatric: acute injury, chronic joint pain, back/neck pain, post-op concerns
2. WHEN detecting red flags THEN the system SHALL identify: open fracture, severe deformity, compartment syndrome signs, cauda equina, neurovascular compromise, suspected septic arthritis, high-energy trauma, fever with joint pain in child
3. WHEN gathering evidence THEN the system SHALL capture: mechanism of injury, weight-bearing ability, focal tenderness map, swelling timeline, prior imaging/therapy, comorbidities, anticoagulants
4. WHEN patients upload attachments THEN the system SHALL support wound/joint photos and prior imaging reports (PDF) with AI requesting standardized views when relevant
5. WHEN determining completion THEN the system SHALL use configurable thresholds + confidence gating per flow

### Requirement 5 - Clinician Review Workspace

**User Story:** As a doctor, I want to rapidly review and finalize chart content so that I can make efficient clinical decisions.

#### Acceptance Criteria

1. WHEN reviewing intake THEN the system SHALL provide single pane: Intake Summary (EN), key symptoms, PMH/Meds/Allergies, ROS hits, Red-flag chip, attachments, timeline
2. WHEN displaying AI suggestions THEN the system SHALL clearly label "AI-generated (not diagnosis)" with confidence and evidence links
3. WHEN finalizing content THEN the system SHALL provide one-click: accept to SOAP, edit inline, request clarification, order follow-up
4. WHEN signing off THEN the system SHALL require e-sign to finalize with full version history and audit
5. WHEN accessing records THEN the system SHALL maintain immutable audit for PHI access and edits

### Requirement 6 - Lightweight EMR Core

**User Story:** As a provider, I want to manage longitudinal records without heavy overhead so that I can focus on patient care.

#### Acceptance Criteria

1. WHEN managing patients THEN the system SHALL provide patient chart: demographics (incl. ABHA optional), encounters, notes, documents, meds/allergies, problem list
2. WHEN searching patients THEN the system SHALL provide fuzzy search across name/phone/MRN/ABHA with dedupe & merge capabilities
3. WHEN editing concurrently THEN the system SHALL provide concurrent-edit safety (optimistic lock + conflict resolver UI)
4. WHEN exporting data THEN the system SHALL support PDF visit note + JSON "FHIR-lite" bundle with vNext FHIR R4 adapter
5. WHEN auditing access THEN the system SHALL maintain immutable audit for PHI access and edits

### Requirement 7 - Communications & Follow-ups

**User Story:** As a doctor, I want to securely clarify and follow up with patients so that I can provide comprehensive care.

#### Acceptance Criteria

1. WHEN communicating with patients THEN the system SHALL provide secure patient portal messaging (no PHI in plain SMS/WhatsApp)
2. WHEN sending messages THEN the system SHALL send deep-link to portal with templates for instructions and PROs
3. WHEN follow-up is needed THEN the system SHALL allow re-opening mini-intakes as needed
4. WHEN communications occur THEN the system SHALL link all comms to encounter with read receipts recorded

### Requirement 8 - Security & Compliance (India-Specific)

**User Story:** As a patient, I want my medical information to be secure and compliant with Indian regulations so that I can trust the system.

#### Acceptance Criteria

1. WHEN processing patient data THEN the system SHALL implement real-time safety classifier + prompt constraints to block diagnosis/medication advice with 100% must-pass eval suite
2. WHEN providing telemedicine services THEN the system SHALL align with Telemedicine Practice Guidelines 2020 (RMP identification, consent, documentation)
3. WHEN handling personal data THEN the system SHALL comply with DPDPA 2023 (notice & consent, purpose limitation, security controls, breach logging, data principal rights)
4. WHEN using data for improvement THEN the system SHALL use de-identified data with tenant-level opt-out capability
5. WHEN storing PHI THEN the system SHALL encrypt at rest (AES-256) and in transit (TLS 1.2+) with app logs excluding PHI
6. IF ABDM/ABHA is enabled THEN the system SHALL use ABDM consent manager patterns for data exchange with consent expiry scopes

### Requirement 9 - Performance & Quality Metrics

**User Story:** As a system operator, I want to monitor system performance and quality so that I can ensure reliable service delivery.

#### Acceptance Criteria

1. WHEN processing requests THEN the system SHALL maintain P95 ≤ 1.5s (text turn), ≤ 3.0s (voice turn)
2. WHEN operating THEN the system SHALL achieve 99.9% monthly availability
3. WHEN scaling THEN the system SHALL support ≥ 200 concurrent intakes with linear scale-out on ECS Fargate
4. WHEN serving users THEN the system SHALL meet WCAG 2.1 AA with captions on by default for voice
5. WHEN processing languages THEN the system SHALL track WER and extraction F1 per language with doctor-output English grammar score ≥ 99%
6. WHEN storing data THEN the system SHALL maintain all PHI in AWS India regions with cross-region DR within India