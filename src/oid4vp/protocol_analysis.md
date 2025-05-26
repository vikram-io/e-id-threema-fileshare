# OID4VP Protocol Analysis for Swiss E-ID Integration

## Overview

The OpenID for Verifiable Presentations (OID4VP) protocol - draft 20 is used in the Swiss E-ID system for credential verification. This document analyzes the key components and flows needed to integrate our file signing application with the Swiss E-ID iOS app.

## Protocol Flow

The OID4VP protocol for the Swiss E-ID system follows these steps:

1. **Verifier Initialization**:
   - Generate a unique request ID
   - Create a presentation definition specifying required credentials
   - Encode the request as a JWT

2. **QR Code Generation**:
   - Encode the request as a URL with appropriate parameters
   - Generate a QR code containing this URL
   - Display to user for scanning with E-ID app

3. **User Interaction**:
   - User scans QR code with E-ID app
   - App processes the request and prompts for consent
   - User selects credentials to share

4. **Callback Processing**:
   - E-ID app sends the presentation to our callback endpoint
   - Our application verifies the presentation
   - Application processes the verification result

5. **Signature Verification**:
   - Verify the cryptographic signature using ECDSA with P-256 curve
   - Validate the credential against the Trust Registry
   - Check for revocation using Token Status List

## Request Format

The OID4VP request must include:

```json
{
  "response_type": "vp_token",
  "client_id": "https://our-app-domain.com/callback",
  "redirect_uri": "https://our-app-domain.com/callback",
  "response_mode": "direct_post",
  "presentation_definition": {
    "id": "unique-request-id",
    "input_descriptors": [
      {
        "id": "swiss-eid-descriptor",
        "format": {
          "jwt_vp": {
            "alg": ["ES256"]
          }
        },
        "constraints": {
          "fields": [
            {
              "path": ["$.type"],
              "filter": {
                "type": "string",
                "pattern": "SwissEID"
              }
            }
          ]
        }
      }
    ]
  },
  "nonce": "random-nonce-value",
  "state": "session-state"
}
```

## Response Format

The expected response will be a JWT containing:

```json
{
  "iss": "did:webvh:user-did",
  "aud": "our-client-id",
  "jti": "unique-response-id",
  "iat": 1621234567,
  "exp": 1621238167,
  "vp": {
    "@context": ["https://www.w3.org/2018/credentials/v1"],
    "type": ["VerifiablePresentation"],
    "verifiableCredential": [
      "encoded-credential-jwt"
    ]
  },
  "nonce": "random-nonce-value-from-request",
  "presentation_submission": {
    "id": "submission-id",
    "definition_id": "unique-request-id-from-request",
    "descriptor_map": [
      {
        "id": "swiss-eid-descriptor",
        "format": "jwt_vp",
        "path": "$.vp.verifiableCredential[0]"
      }
    ]
  }
}
```

## QR Code Requirements

The QR code must encode a URL with the following format:

```
openid://vp?request=encoded-jwt-request
```

Alternatively, for web-based flows:

```
https://wallet-provider.example.org/vp?request=encoded-jwt-request
```

## Cryptographic Requirements

- **Signature Algorithm**: ECDSA with P-256 curve
- **JWT Signing**: ES256 algorithm
- **Nonce**: Required for replay protection
- **State**: Required for session binding

## Implementation Considerations

1. **DID Resolution**:
   - Need to resolve the user's DID to verify signatures
   - Must use the did:webvh method

2. **Callback Security**:
   - Ensure callback endpoint is properly secured
   - Validate all incoming requests
   - Implement proper error handling

3. **Session Management**:
   - Maintain session state during the verification flow
   - Associate verification results with the correct file

4. **Error Handling**:
   - Handle timeouts if user doesn't complete the flow
   - Provide clear error messages
   - Implement retry mechanisms

## Next Steps

1. Implement JWT generation for OID4VP requests
2. Create QR code generation with proper encoding
3. Set up callback endpoint for receiving presentations
4. Implement signature verification logic
5. Integrate with file signing workflow
