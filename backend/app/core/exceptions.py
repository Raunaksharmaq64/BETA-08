"""
RIGHT FIT Core — Standard Domain Exceptions Placeholder
Status: ARCHITECTURE SETUP PHASE (Template)
"""


class RightFitBaseException(Exception):
    """Base exception for all RIGHT FIT domain errors."""
    pass


class ResourceNotFoundException(RightFitBaseException):
    """Raised when an entity is not found."""
    pass


class ServiceUnavailableException(RightFitBaseException):
    """Raised when an external satellite service or adapter fails."""
    pass

