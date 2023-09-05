# write_messages.py

from jinja2 import Environment, PackageLoader

jinja_environment = Environment(
    loader=PackageLoader("datafest_archive", "templates"), autoescape=True
)
