class ModuleRegistry:
    def __init__(self):
        self._modules = {}

    def register(self, module):
        self._modules[module.name] = module

    def all(self):
        return list(self._modules.values())

    def get(self, name):
        return self._modules.get(name)


registry = ModuleRegistry()
