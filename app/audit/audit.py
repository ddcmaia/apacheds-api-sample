import logging
import os

from config import AUDIT_LOG, AUDIT_BUCKET, ENABLE_AUDIT_BUCKET

LOG_FILE = AUDIT_LOG
_logger = logging.getLogger('audit')
if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    handler = logging.FileHandler(LOG_FILE)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

_bucket = None
if ENABLE_AUDIT_BUCKET and AUDIT_BUCKET:
    try:
        from google.cloud import storage
        _bucket = storage.Client().bucket(AUDIT_BUCKET)
    except Exception:
        _bucket = None


def _upload_to_bucket():
    if ENABLE_AUDIT_BUCKET and _bucket:
        blob = _bucket.blob(os.path.basename(LOG_FILE))
        blob.upload_from_filename(LOG_FILE)


def log_action(action, **details):
    msg = f"{action}: " + ", ".join(f"{k}={v}" for k, v in details.items())
    _logger.info(msg)
    _upload_to_bucket()
