import toml
import sys

from .abstract_info import AbstractInfo

class XPathInfo(AbstractInfo):
    def __init__(self) -> None:
        super().__init__()
        self.java_package = ""
        self.java_class = ""

    @property
    def root_path(self) -> str:
        return "%sXPath_TS_%s" % (self.name, self.eb_version)

    @property
    def java_package_path(self) -> str:
        return self.java_package.replace(".", "/")
    
    def _parse_toml_data(self, data):
        super()._parse_toml_data(data)

        self.java_package = data['java']['package']
        self.java_class = data['java']['class']
        #self.dump()

    def parse(self, filename):
        parsed_toml = toml.load(filename)
        self._parse_toml_data(parsed_toml)

    def dump(self):
        super().dump()

        print("Java Package   : %s" % self.java_package)
        print("Java Class     : %s" % self.java_class)
        sys.exit(1)