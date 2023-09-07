"""autopop: Auto Populate utils."""

__version__ = '1.0'

from .aws_util import get_sm_client, get_s3_client
from .aws_util import get_creds, get_secret_key, persist_to_s3
from .recording_util import get_recording_data

__all__ = [
    'get_s3_client',
    'get_sm_client',
    'get_creds',
    'get_secret_key',
    'persist_to_s3',
    'get_recording_data'
]