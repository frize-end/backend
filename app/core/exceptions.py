class BussinessException(Exception):
    """
    自定义业务异常
    用于抛出所有预期内的业务逻辑错误，由全局异常处理器统一拦截返回
    """
    def __init__(self, message, code):
        self.message = message
        self.code = code