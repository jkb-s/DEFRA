from json import loads, dumps
from types import SimpleNamespace
from dataclasses import dataclass, field
from os import path, walk


class JSON:
    def __str__(self):
        return dumps(self.__dict__, indent=4)

    def json(self):
        return self.__dict__



@dataclass
class DTechnique(JSON):
    id: str
    name: str
    system: str
    type: str = "Defense Technique"
    intid: int = None
    filename: str = None
    description: str = ""
    created: str = ""
    severity: str = ""
    fpratio: float = None
    tags: list = field(default_factory=list)
    references: list = field(default_factory=list)
    detects: dict = field(default_factory=dict)
    uses: list = field(default_factory=list)
    scope: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.intid:
            self.intid = int(self.id.split('.')[-1])
        if not self.filename:
            self.filename = self.name.replace(' ', '-').replace('\\', '').replace('/', '') + ".json"
        
    def write(self, parentpath):
        filepath = path.join(parentpath, self.id.split('.')[1], self.filename)
        with open(filepath, 'w+') as file:
            file.write(dumps(self.__dict__, indent=4))
            file.close()


    
@dataclass
class DSystem(JSON):
    id: str
    name: str
    type: str = "Defense System"
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

class Defend:

    def __init__(self, attack):
        self.attack = attack

        # init functions
        self.load_defense_systems()                       # self.systems
        self.load_defense_techniques()                    # self.techniques

    def load_defense_systems(self):
        self.systems = {}
        systemspath = path.join('.', self.attack.cfg.defend_systems)
        for root, subdirectories, files in walk(systemspath):
            for file in files:
                if file[-5:] == ".json":
                    filename = path.join(root, file)
                    with open(filename, 'r') as fobj:
                        data = loads(fobj.read())
                        fobj.close()
                        self.systems.update({
                            data['id']: DSystem(**data)
                        })

    def load_defense_techniques(self):
        self.techniques = {}
        techniquespath = path.join('.', self.attack.cfg.defend_techniques)
        for root, subdirectories, files in walk(techniquespath):
            for file in files:
                if file[-5:] == ".json":
                    filename = path.join(root, file)
                    with open(filename, 'r') as fobj:
                        data = loads(fobj.read())
                        fobj.close()
                        self.techniques.update({
                            data['id']: DTechnique(**data)
                        })