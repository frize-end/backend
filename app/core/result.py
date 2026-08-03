class Result:
    @staticmethod
    def success(data=None,message="操作成功",code=200):
        """成功响应：默认状态码200，可自定义提示和数据"""
        return{
            "code":code,
            "message":message,
            "data":data
        }

    @staticmethod
    def error(message="操作失败", code=400, data=None):
        """失败响应：默认状态码400，可自定义错误码和提示"""
        return{
            "code":code,
            "message":message,
            "data":data
        }