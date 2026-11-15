"""Secure OTP generation, storage, and verification."""
import hashlib
import secrets
from datetime import datetime, timedelta

from models.otp import OTPCode


OTP_LIFETIME_MINUTES = 5
MAX_ATTEMPTS = 5
RESEND_COOLDOWN_SECONDS = 60


def _hash_code(code):
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def create_otp(user_id, db):
    latest = OTPCode.query.filter_by(user_id=user_id).order_by(OTPCode.sent_at.desc()).first()
    if latest and (datetime.utcnow() - latest.sent_at).total_seconds() < RESEND_COOLDOWN_SECONDS:
        raise ValueError("Please wait before requesting another code.")
    code = f"{secrets.randbelow(1_000_000):06d}"
    otp = OTPCode(user_id=user_id, code_hash=_hash_code(code), expires_at=datetime.utcnow() + timedelta(minutes=OTP_LIFETIME_MINUTES))
    db.session.add(otp)
    db.session.commit()
    return code


def verify_otp(user_id, submitted_code, db):
    otp = OTPCode.query.filter_by(user_id=user_id, used_at=None).order_by(OTPCode.sent_at.desc()).first()
    if not otp or otp.expires_at < datetime.utcnow() or otp.attempts >= MAX_ATTEMPTS:
        return False
    otp.attempts += 1
    valid = secrets.compare_digest(otp.code_hash, _hash_code(submitted_code.strip()))
    if valid:
        otp.used_at = datetime.utcnow()
    db.session.commit()
    return valid

