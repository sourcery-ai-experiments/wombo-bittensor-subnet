import os

KEEP_ALIVE_TIMEOUT = int(os.getenv("KEEP_ALIVE_TIMEOUT", str(120)))
AXON_REQUEST_TIMEOUT = int(os.getenv("AXON_REQUEST_TIMEOUT", str(60)))
CLIENT_REQUEST_TIMEOUT = int(os.getenv("CLIENT_REQUEST_TIMEOUT", str(60)))
