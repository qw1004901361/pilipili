# coding=UTF-8
class Redprint:
    """
    原来使用Blueprint，只需要Blueprint.route，但现在我们模仿Blueprint构建Redprint，
    需要调用Redprint.route，再调用register，完成总的路由功能
    """

    def __init__(self, name):
        self.name = name
        self.mound = []

    def route(self, rule, **options):
        def decorator(f):
            """
            模仿Blueprint.route所做的事情，代码如下：
            endpoint = options.pop("endpoint", f.__name__)
            self.add_url_rule(rule, endpoint, f, **options)
            但此时我们没有Blueprint对象,先保存起来，再以后调用
            :param f:
            :return:f
            """
            self.mound.append((f, rule, options))
            return f

        return decorator

    def register(self, bp, url_prefix=None):
        """
        此时，我们有了Blueprint对象，将Redprint定义的route中的参数提取出来，
        进行Blueprint.route所做的事情
        :param bp: Blueprint对象
        :param url_prefix: URL前缀
        :return: None
        """
        if url_prefix is None:
            url_prefix = "/" + self.name
        for f, rule, options in self.mound:
            endpoint = self.name + "+" + options.pop("endpoint", f.__name__)
            # options是dict，尝试取key为endpoint的值，否则取key为f.__name__（视图函数）的值
            # endpoint = options.pop("endpoint", f.__name__)
            bp.add_url_rule(url_prefix + rule, endpoint, f, **options)
