# E-ID File Signing Web Application - Todo List

## Requirements
- [x] Clarify webapp requirements and E-ID integration expectations
- [x] Select and initialize webapp template (Flask)
- [x] Create uploads directory for file storage

## Implementation Tasks
- [x] Implement file upload functionality
  - [x] Create upload form with file input
  - [x] Set up file size limit (100MB)
  - [x] Implement secure file storage
  - [x] Add file expiration (24h temporary storage)
- [x] Implement E-ID signing integration
  - [x] Research OID4VP protocol integration
  - [x] Create signing endpoint
  - [x] Implement file hash generation
  - [x] Set up E-ID authentication flow
- [x] Implement Threema link sharing
  - [x] Install and configure Threema SDK
  - [x] Create shareable links for signed files
  - [x] Implement Threema message sending
- [x] Implement file verification with E-ID
  - [x] Create verification page
  - [x] Implement signature validation
  - [x] Display verification results

## Deployment
- [x] Test all functionality
- [x] Deploy web application
- [x] Document usage instructions
