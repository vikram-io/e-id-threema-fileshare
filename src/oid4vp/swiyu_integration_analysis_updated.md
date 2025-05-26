# SWIYU App Integration Analysis - Updated for Presentation Flow

## Key Findings from User Testing

Based on user testing feedback, we've identified two critical issues:

1. **QR Code Protocol Issue**: Tapping on the QR code opens Authenticator instead of the SWIYU app
2. **Credential Flow Issue**: The SWIYU app shows "invalid credentials, cannot be added" because the user already has credentials

## Corrected QR Code Format Requirements

The QR code must use the correct protocol format for presentation requests (not credential offers):

1. **Correct Protocol Format**: Must use `swiyu://present?request_uri=` instead of `swiyu://oidc` or `swiyu://auth`
2. **Presentation Request**: The payload must be structured as a presentation request to use existing credentials, not as a credential offer
3. **Deep Linking**: For iOS devices, the deep link must correctly target the SWIYU app, not Authenticator

## OID4VP Protocol Requirements for Presentation Flow

The OID4VP (OpenID for Verifiable Presentations) protocol implementation must be adjusted:

1. **JWT Structure**: The request must be structured as a presentation request, not a credential offer
2. **Presentation Definition**: Must include the correct presentation definition to request existing credentials
3. **Response Handling**: The callback must properly handle presentation responses, not credential issuance responses

## Implementation Updates

To properly integrate with the SWIYU app using existing credentials:

1. Update the QR code generation to use the `swiyu://present` protocol format
2. Modify the JWT payload to request a presentation, not offer credentials
3. Update the callback endpoints to handle presentation responses
4. Ensure deep linking correctly targets the SWIYU app on iOS
5. Update all UI references and instructions to reflect the presentation flow

This analysis will guide the implementation of the corrected SWIYU app integration in the next steps.
