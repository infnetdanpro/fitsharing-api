from jinja2 import Environment, PackageLoader, select_autoescape
# env = Environment(
#     loader=PackageLoader("application"),
#     autoescape=select_autoescape()
# )


class Template:
    def __init__(self, name: str, context: dict):
        self.name = name
        self.context = context

    def render(self):
        template = env.get_template(f"{self.name}.html")
        return template.render(**self.context)
