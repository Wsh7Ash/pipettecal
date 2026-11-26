# Project Specification — pipettecal

## Vision
Gravimetric pipette calibration certificate with independent verification.

## Target audience
Lab technicians, QA, students.

## Problem
Pipette calibration requires computing delivered volume from mass with
buoyancy correction; manual calculation is error-prone and rarely verified.

## Existing alternatives
Artel PCS (commercial), various online calculators. Few open-source tools
produce a verifiable certificate.

## Differentiation
Buoyancy-corrected per-replicate volumes, statistics, pass/fail with reasons,
embedded input, independent verify command.

## Core functionality
Parse/validate input, compute volumes, statistics, verdict, report, verify.

## Architecture
model -> calibrate -> report -> cli.

## Testing
Unit tests for model, calibrate, verify, CLI demo.

## Limitations
Approximate water density; no evaporation/operator/balance calibration.