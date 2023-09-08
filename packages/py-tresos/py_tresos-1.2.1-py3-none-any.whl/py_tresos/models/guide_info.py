import toml

from .abstract_info import AbstractInfo

class GuideInfo(AbstractInfo):
    def __init__(self) -> None:
        super().__init__()

        self.tresos_root = ""
        self.ar_package = ""
        self.package = ""
        self.backend_class = ""
        self.page_class = ""
        self.push_event_class = ""
        self.push_operation_class =""
        self.sidebar_category = ""
        self.sidebar_label = ""
        self.sidebar_tooltip = ""

    @property
    def package_path(self) -> str:
        return self.package.replace(".", "/")

    def _parse_toml_data(self, data):
        super()._parse_toml_data(data)

        self.ar_package = data['component']['ar_package']
        self.tresos_root = data['component']['tresos_root']
        self.package = data['component']['package']
        self.backend_class = data['class']['backend']
        self.page_class = data['class']['page']
        if 'push_event' in data['class']:        
            self.push_event_class = data['class']['push_event']
        if 'push_operation' in data['class']:
            self.push_operation_class = data['class']['push_operation']
        self.sidebar_category = data['sidebar']['category']
        self.sidebar_label = data['sidebar']['label']

        if ('tooltip' in data['sidebar']):
            self.sidebar_tooltip = data['sidebar']['tooltip']

    def parse(self, filename):
        parsed_toml = toml.load(filename)
        self._parse_toml_data(parsed_toml)
    
    def dump(self):
        super().dump()

        print("Backend          : %s" % self.backend_class)
        print("Page             : %s" % self.page_class)
        print("Push Event       : %s" % self.push_event_class)
        print("Push Operation   : %s" % self.push_operation_class)
        print("Sidebar Category : %s" % self.sidebar_category)
        print("Sidebar Label    : %s" % self.sidebar_label)
