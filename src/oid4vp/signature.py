import jwt
import time
import uuid
import json
import requests
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat, NoEncryption

class SwiyuSignatureService:
    """
    Service for handling SWIYU presentation requests and signature verification
    """
    
    def __init__(self, private_key_path=None):
        """
        Initialize the signature service
        
        Args:
            private_key_path: Path to the private key file for signing
        """
        self.private_key = None
        if private_key_path:
            with open(private_key_path, 'rb') as key_file:
                self.private_key = load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        else:
            # Generate a new key for testing if none provided
            self.private_key = ec.generate_private_key(ec.SECP256R1())
        
        # Store the public key in PEM format
        self.public_key_pem = self.private_key.public_key().public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
    def create_presentation_request(self, file_id, callback_url, nonce=None):
        """
        Create a presentation request for the SWIYU App to use existing credentials
        
        Args:
            file_id: The ID of the file to be signed
            callback_url: The callback URL for the presentation response
            nonce: Optional nonce for the request
            
        Returns:
            JWT token for the presentation request
        """
        # Create a nonce if not provided
        if not nonce:
            nonce = str(uuid.uuid4())
        
        # Current time
        now = int(time.time())
        
        # Create the JWT payload for a presentation request (not credential offer)
        payload = {
            "iss": f"did:example:verifier:{file_id}",  # Issuer identifier
            "iat": now,  # Issued at
            "exp": now + 3600,  # Expires in 1 hour
            "nbf": now,  # Not valid before now
            "jti": nonce,  # JWT ID
            "response_type": "vp_token",  # Request a verifiable presentation token
            "response_mode": "direct_post",  # Direct post response mode
            "client_id": callback_url,  # Client ID is the callback URL
            "redirect_uri": f"{callback_url}/callback",  # Redirect URI
            "presentation_definition": {
                "id": f"sign-request-{file_id}",
                "input_descriptors": [
                    {
                        "id": "swiyu-credential",
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
                                        "pattern": "VerifiablePresentation"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        # Create the JWT headers
        headers = {
            "typ": "JWT",
            "alg": "ES256",
            "kid": f"did:example:verifier:{file_id}#key-1"
        }
        
        # Sign the JWT
        token = jwt.encode(
            payload=payload,
            key=self.private_key,
            algorithm="ES256",
            headers=headers
        )
        
        return token
    
    def verify_presentation_response(self, response_token):
        """
        Verify a presentation response from the SWIYU App
        
        Args:
            response_token: The JWT token from the presentation response
            
        Returns:
            Tuple of (is_valid, claims) where is_valid is a boolean and claims is the decoded token
        """
        try:
            # In a real implementation, you would:
            # 1. Verify the signature using the public key of the issuer
            # 2. Check the token hasn't expired
            # 3. Validate the claims against your requirements
            
            # For this proof of concept, we'll just decode the token without verification
            # and assume it's valid if it can be decoded
            decoded = jwt.decode(
                response_token,
                options={"verify_signature": False}
            )
            
            # Check if this is a valid presentation
            if "vp" not in decoded:
                return False, {"error": "Not a valid presentation response"}
            
            return True, decoded
            
        except Exception as e:
            return False, {"error": str(e)}
    
    def sign_file(self, file_path, holder_did):
        """
        Sign a file using the SWIYU presentation response
        
        Args:
            file_path: Path to the file to sign
            holder_did: DID of the holder who authenticated
            
        Returns:
            Signature data
        """
        # In a real implementation, you would:
        # 1. Hash the file
        # 2. Sign the hash with the private key
        # 3. Create a signature object with metadata
        
        # For this proof of concept, we'll create a mock signature
        with open(file_path, 'rb') as f:
            file_hash = hashes.Hash(hashes.SHA256())
            # Read in chunks to handle large files
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
            digest = file_hash.finalize()
        
        # Create a signature timestamp
        timestamp = int(time.time())
        
        # Create a signature object
        signature = {
            "file_hash": base64.b64encode(digest).decode('utf-8'),
            "algorithm": "SHA256withECDSA",
            "signer": holder_did,
            "timestamp": timestamp,
            "signature_type": "swiyu-presentation"
        }
        
        return signature
    
    def verify_file_signature(self, file_path, signature_data):
        """
        Verify a file signature
        
        Args:
            file_path: Path to the file to verify
            signature_data: Signature data from sign_file
            
        Returns:
            Boolean indicating if the signature is valid
        """
        # In a real implementation, you would:
        # 1. Hash the file
        # 2. Verify the signature using the public key of the signer
        # 3. Check the signature metadata
        
        # For this proof of concept, we'll just check if the file hash matches
        with open(file_path, 'rb') as f:
            file_hash = hashes.Hash(hashes.SHA256())
            # Read in chunks to handle large files
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
            digest = file_hash.finalize()
        
        # Compare the hash
        expected_hash = base64.b64decode(signature_data["file_hash"])
        return digest == expected_hash
