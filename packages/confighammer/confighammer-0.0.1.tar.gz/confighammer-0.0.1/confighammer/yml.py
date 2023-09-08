
import yaml
class YAML():
    file=None
    config=None
    def __init__(self, file=None, config=None):
        self.file = file
        self.config = config
    def load(self):
        if not self.file:
            return "No-YAML-file-defined"
        else:
            with open(self.file) as f:
                _config = yaml.full_load(f)
            self.config = _config
    def write(self):
        pass

"""

y = YAML('/root/.gehc/config.yml')
y.load()
y.config

"""