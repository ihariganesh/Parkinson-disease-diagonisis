from typing import Optional, Any


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(AppException):
    """Resource not found error"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )


class UnauthorizedError(AppException):
    """Unauthorized access error"""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED"
        )


class ForbiddenError(AppException):
    """Forbidden access error"""
    
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN"
        )


class FileUploadError(AppException):
    """File upload error"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            details=details
        )