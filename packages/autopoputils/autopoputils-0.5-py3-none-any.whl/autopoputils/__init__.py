"""autopop: Auto Populate utils."""

__version__ = '0.5'

from .aws_util import get_sm_client, get_creds, get_secret_key
from .recording_util import get_recording_data

__all__ = [
    'get_sm_client',
    'get_creds',
    'get_secret_key',
    'get_recording_data'
]