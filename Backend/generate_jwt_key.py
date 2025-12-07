"""
Generate a secure JWT secret key for production use
Run this script once and copy the generated key to your .env file
"""
import secrets
import string

def generate_secret_key(length=64):
    """Generate a cryptographically secure secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret_key

if __name__ == "__main__":
    key = generate_secret_key()
    print("=" * 80)
    print("🔐 Your Secure JWT Secret Key:")
    print("=" * 80)
    print(f"\n{key}\n")
    print("=" * 80)
    print("\n📝 Add this to your Backend/.env file:")
    print(f"JWT_SECRET_KEY={key}")
    print("\n⚠️  Keep this key secret and never commit it to version control!")
    print("=" * 80)
