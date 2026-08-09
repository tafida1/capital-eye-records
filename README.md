# 👁️ Capital Eye Hospital Records System

### Comprehensive Hospital & Ophthalmology Records Management Platform

**Capital Eye Hospital Records System (CEHRS)** is a multi-user, database-driven healthcare management application developed to digitize and streamline clinical, administrative, financial, and operational workflows within an eye clinic/hospital environment.

The system is designed for practical deployment within a healthcare facility and supports multiple authorized users working simultaneously over a secure local network.

---

## 🏥 Project Overview

Capital Eye Hospital Records System provides a centralized platform for managing patient information and day-to-day hospital operations.

The system brings together patient registration, clinical records, ophthalmology workflows, appointments, surgery management, billing, reporting, audit trails, user administration, notifications, and system backup functionality within one integrated application.

The application is designed to support both **local/offline clinic deployment** and future expansion toward cloud-based infrastructure.

---

# ✨ Major Features

## 👤 Patient & Family Records

- Patient registration and profile management
- Unique patient records
- Family/group records
- Patient demographic information
- Medical history
- Patient search
- Medical timeline
- Clinical summaries
- Patient document and attachment management

---

## 🩺 Clinical & Ophthalmology Records

- Patient visits and consultations
- Ophthalmology examination records
- Clinical findings
- Diagnosis management
- Prescription management
- Procedures
- Medical notes
- Longitudinal patient history
- Clinical attachments

---

## 👁️ Surgery Management

- Surgery scheduling
- Surgery records
- Surgery status tracking
- Surgical reporting
- Date-based surgery filtering
- PDF and Excel surgery reports

---

## 📅 Appointment & Queue Management

- Appointment scheduling
- Appointment records
- Patient queue management
- Appointment status tracking
- Appointment reports
- Daily operational workflow support

---

## 💳 Billing & Financial Management

- Patient billing
- Financial records
- Payment-related workflows
- Financial reporting
- Filtered financial reports
- PDF report generation
- Excel report generation

---

## 📊 Reports & Analytics

The system provides operational and management reporting capabilities including:

- Clinical reports
- Financial reports
- Appointment reports
- Surgery reports
- Date-range filtering
- PDF exports
- Excel exports

---

## 👥 User & Role Management

The application supports multiple user roles including:

- Super Administrator
- Hospital Administrator
- Receptionist
- Doctor / Ophthalmologist
- Nurse
- Cashier / Accountant
- Records Officer
- Laboratory / Procedure Staff
- Viewer / Auditor

Access to functionality is controlled through **Role-Based Access Control (RBAC)**.

---

## 🔐 Security & Accountability

Security and accountability features include:

- User authentication
- Role-based authorization
- Password management
- Audit logging
- User activity tracking
- IP address logging
- User-agent logging
- Controlled administrative access
- Secure operational workflows

---

## 🔔 Notifications

The system includes notification functionality for communicating important operational information to authorized users.

---

## 💾 Backup & Recovery

Capital Eye Hospital Records System includes backup-oriented functionality to support:

- Local data protection
- Administrative backups
- External-drive backup workflows
- Future cloud-backup integration
- Recovery planning

---

# 🌐 Local Network / Offline Deployment

One of the key architectural goals of CEHRS is the ability to operate within a hospital without requiring continuous internet access.

The application can be deployed on a designated clinic server computer and accessed by authorized devices connected to the hospital's local Wi-Fi/LAN network.

### Deployment Architecture

```text
                    ┌──────────────────────┐
                    │  Clinic Server PC    │
                    │                      │
                    │ Django Application   │
                    │ Database             │
                    │ Waitress Server      │
                    └──────────┬───────────┘
                               │
                         Local Router
                         Wi-Fi / LAN
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    Reception PC          Doctor PC           Accounts PC
          │                    │                    │
       Browser              Browser              Browser
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                       Tablets / Laptops
