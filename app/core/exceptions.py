class ResourceNotFound(Exception):
    """资源不存在 (404)"""
    pass

class PermissionDenied(Exception):
    """权限不足 (403)"""
    pass

class BusinessError(Exception):
    """通用业务错误 (400)"""
    pass

class FileConflictError(Exception):
    """文件冲突错误 (409)"""
    pass

class InvalidFileError(Exception):
    """无效文件错误 (422)"""
    pass

class InternalServerError(Exception):
    """服务器内部错误 (500)"""
    pass
