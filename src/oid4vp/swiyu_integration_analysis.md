# SWIYU App Integration Analysis

## QR Code Format Requirements

Based on the SWIYU documentation, I've identified the following key requirements for QR code generation that will be compatible with the SWIYU app:

1. **QR Code Protocol Format**: The QR code must use the `swiyu://oidc` protocol format instead of the generic `swiyu://auth` format.

2. **Beta Credential Type**: The credential type must be specified as `"vct": "betaid-sdjwt"` in the payload.

3. **Signature Algorithm**: Must use `"_sd_alg": { "value": "sha-256" }` and `"alg": "ES256"` with P-256 curve.

4. **Issuer Identification**: The issuer must be properly identified with a valid DID format as shown in the example.

5. **Mobile Deep Linking**: For iOS devices, the QR code should be tappable to directly launch the SWIYU app.

## OID4VP Protocol Requirements

The OID4VP (OpenID for Verifiable Presentations) protocol implementation must include:

1. **JWT Structure**: The authentication request must follow the SD-JWT VC format with proper headers and claims.

2. **Callback Endpoints**: Must implement secure callback endpoints to receive and process authentication responses.

3. **Beta Credential Flow**: The application must support the beta credential flow, which differs from the production e-ID flow.

4. **Status Verification**: Must include proper status verification using the status list mechanism.

## Implementation Plan

To properly integrate with the SWIYU app:

1. Update the QR code generation to use the correct `swiyu://oidc` protocol format
2. Implement tap-to-launch functionality for iOS devices
3. Update all UI references from "Swiss E-ID" to "SWIYU App"
4. Implement the proper JWT generation for authentication requests
5. Set up secure callback endpoints for the OID4VP protocol
6. Implement proper credential verification

This analysis will guide the implementation of the real SWIYU app integration in the next steps.
