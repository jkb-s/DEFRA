from json import loads, dumps
from types import SimpleNamespace
from dataclasses import dataclass, field

@dataclass
class DTechnique:
    name: str
    id: str
    system: str
    description: str = ""
    tags: list = field(default_factory=list)
    references: list = field(default_factory=list)
    detects: dict = field(default_factory=dict)
    uses: list = field(default_factory=list)
    scope: dict = field(default_factory=dict)
    
    def __post_init__(self):
        self.intid = int(self.id.split('.')[-1])
        self.filename = self.name.replace(' ', '-').replace('\\', '').replace('/', '') + ".json"
        
    def write(self):
        filepath = path.join(self.id.split('.')[1], self.filename)
        with open(filepath, 'w+') as file:
            file.write(dumps(self.__dict__, indent=4))
            file.close()
    
@dataclass
class DSystem:
    id: str
    name: str
    description: str = ""
    top_id: int = 0
    data_sources: list = field(default_factory=list)
    
    def get_top_index(self):
        return self.top_id
    
    # update top index
    def set_top_index(self, top=None):
        if top:
            self.top_id = top
        else:
            self.top_id += 1
    
    def write(self):
        filepath = (self.id + ".json")
        with open(filepath, 'w+') as file:
            file.write(dumps(self.__dict__, indent=4))
            file.close()