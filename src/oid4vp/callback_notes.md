# E-ID Integration Callback Endpoint

To complete the integration with the Swiss E-ID app, we need to implement a callback endpoint that will receive the authentication response from the E-ID app after the user scans the QR code and approves the authentication.

This endpoint will:
1. Receive the presentation JWT from the E-ID app
2. Verify the presentation using our OID4VP service
3. If valid, sign the file using our signature service
4. Update the file metadata with the signature information
5. Return a success response to the E-ID app
6. Notify the web application that the signing is complete

Let's implement this endpoint now.
