# Security Alert: Suspicious Sudo Usage

This document records a Grafana security alert observed in the DARWIN system.

## Alert Details

- **Alert Name:** Suspicious Sudo Usage
- **State:** Alerting
- **Severity:** critical
- **Dashboard UID:** adfwqwj
- **Panel ID:** 1
- **Value:** 1
- **Created:** 2026-04-09 16:29:10

## Description

A process initiated a `sudo` request. Verify whether this activity was authorized.

## Summary

- **Summary:** Sudo command detected on Darwin-System!

## Notes

- This alert is generated when DARWIN detects a `sudo` invocation in the monitored process stream.
- The current Grafana rule is intended to highlight privilege escalation attempts and prompt human review.
