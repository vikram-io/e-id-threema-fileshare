import jwt
import time
import uuid
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import utils

class SignatureService:
    def __init__(self):
        # Initialize cryptographic keys
        self._init_keys()
    
    def _init_keys(self):
        """Initialize or load cryptographic keys for signing"""
        # In a production environment, these would be securely stored
        # For this implementation, we'll generate new keys each time
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        
        # Get the public key in PEM format for verification
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
    def generate_file_hash(self, file_path):
        """
        Generate a SHA-256 hash of the file content
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            str: Base64-encoded hash of the file
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        # Get the digest and encode as base64
        digest = sha256_hash.digest()
        return base64.b64encode(digest).decode('utf-8')
    
    def sign_file(self, file_path, user_did):
        """
        Create a cryptographic signature for a file
        
        Args:
            file_path (str): Path to the file
            user_did (str): DID of the user who authenticated
            
        Returns:
            dict: Signature data including JWT
        """
        # Generate file hash
        file_hash = self.generate_file_hash(file_path)
        
        # Create signature payload
        payload = {
            "iss": "did:webvh:verifier",  # In production, this would be our actual DID
            "sub": user_did,
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400,  # 24 hours
            "jti": str(uuid.uuid4()),
            "file_hash": file_hash,
            "hash_alg": "SHA-256"
        }
        
        # In a real implementation, we would sign with our private key
        # For this implementation, we'll use a simple JWT
        signature_jwt = jwt.encode(payload, "secret_key", algorithm="HS256")
        
        return {
            "jwt": signature_jwt,
            "file_hash": file_hash,
            "user_did": user_did,
            "timestamp": int(time.time())
        }
    
    def verify_signature(self, signature_jwt, file_path):
        """
        Verify a file signature
        
        Args:
            signature_jwt (str): JWT containing the signature
            file_path (str): Path to the file
            
        Returns:
            dict: Verification result
        """
        try:
            # In a real implementation, we would verify the JWT signature
            # For this implementation, we'll decode without verification
            signature_data = jwt.decode(
                signature_jwt, 
                options={"verify_signature": False}
            )
            
            # Generate file hash
            file_hash = self.generate_file_hash(file_path)
            
            # Compare with the hash in the signature
            if signature_data.get("file_hash") != file_hash:
                return {
                    "success": False,
                    "error": "File hash mismatch"
                }
            
            # In a real implementation, we would:
            # 1. Verify the JWT signature using the issuer's public key
            # 2. Validate the issuer's DID against the Trust Registry
            # 3. Check for revocation
            
            return {
                "success": True,
                "user_did": signature_data.get("sub"),
                "timestamp": signature_data.get("iat")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Singleton instance
signature_service = SignatureService()
