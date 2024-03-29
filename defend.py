from json import loads, dumps
from types import SimpleNamespace
from dataclasses import dataclass, field
from os import path, walk, makedirs
from datetime import datetime
from dateutil import parser
from pyvis.network import Network
import math
import plotly.express as px
from pandas import DataFrame as DF



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
    created: datetime = None
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
        dir = path.join(parentpath, self.id.split('.')[1])
        if not path.exists(dir):
            makedirs(dir)
        filepath = path.join(parentpath, self.id.split('.')[1], self.filename)
        with open(filepath, 'w+') as file:
            file.write(dumps(self.__dict__, indent=4))
            file.close()

    def core(self):
        core_data = {}
        for key in ['id', 'name', 'description', 'created', 'severity', 'fpratio']:
            core_data.update({
                key: self.__dict__[key]
            })
        return core_data

    
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
        self.cfg = attack.cfg

        # init functions
        self.load_defense_systems()                       # self.systems
        self.load_defense_techniques()                    # self.techniques
        self.index_techniques_per_system()                # self.techniques_per_system
        self.index_techniques_per_scope()                 # self.techniques_per_scope
        self.index_techniques_per_attack_techniques()     # self.techniques_per_attack_techniques
        self.index_techniques_per_severity()              # self.techniques_per_severity
        self.index_techniques_per_datasource()            # self.techniques_per_datasource

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
                        data['created'] = parser.parse(data['created'])
                        self.techniques.update({
                            data['id']: DTechnique(**data)
                        })

    def index_techniques_per_system(self):
        self.techniques_per_system = {}
        for tech in self.techniques:
            sys = tech.split('.')[1]
            if sys not in self.techniques_per_system:
                self.techniques_per_system.update({
                    sys : [tech]
                })
            else:
                self.techniques_per_system[sys].append(tech)
    
    def index_techniques_per_scope(self):
        self.techniques_per_scope = {}
        for tech in self.techniques:
            dtech = self.techniques[tech]
            for key in dtech.scope:
                if key not in self.techniques_per_scope:
                    self.techniques_per_scope.update({key: {}})
                    
                for value in dtech.scope[key]:
                    if value not in self.techniques_per_scope[key]:
                        self.techniques_per_scope[key].update({
                            value: [tech]
                        })
                    else:
                        self.techniques_per_scope[key][value].append(tech)

    def index_techniques_per_attack_techniques(self):
        self.techniques_per_attack_techniques = {}
        for dtech in self.techniques:   
            for atech in self.techniques[dtech].detects:
                if atech not in self.techniques_per_attack_techniques:
                    self.techniques_per_attack_techniques.update({
                        atech: [dtech]
                    })
                else:
                    self.techniques_per_attack_techniques[atech].append(dtech)

    def index_techniques_per_severity(self):
        self.techniques_per_severity = {}
        for dtech in self.techniques:
            if self.techniques[dtech].severity not in self.techniques_per_severity:
                self.techniques_per_severity.update({
                    self.techniques[dtech].severity : [dtech]
                })
            else:
                self.techniques_per_severity[
                    self.techniques[dtech].severity
                ].append(dtech)

    def index_techniques_per_datasource(self):
        self.techniques_per_datasource = {}
        for dtech in self.techniques:
            for datacomponent in self.techniques[dtech].uses:
                data_source = datacomponent.split(': ')[0]
                data_component = datacomponent.split(': ')[1]
            
                if data_source not in self.techniques_per_datasource:
                    self.techniques_per_datasource.update({
                        data_source: { data_component: [dtech] }
                    })
                else:
                    if data_component not in self.techniques_per_datasource[data_source]:
                        self.techniques_per_datasource[data_source].update({
                            data_component: [dtech]
                        })
                    else:
                        self.techniques_per_datasource[data_source][data_component].append(dtech)

    def chart_attack_techniques_per_tactic(self):

        records = {}
        for tac in self.cfg.tactics_order:
            records.update({tac: 0})
        
        for tech in self.attack.techniques:
            for tac in self.attack.techniques[tech].tactics:
                records[tac] += 1

        records_arr = []
        for tac in records:
            records_arr.append({'tactic': tac, 'techniques count': records[tac]})

        df = DF.from_records(records_arr)

        

        fig = px.bar(df, 
                    x='tactic', y='techniques count', 
                    color='techniques count', 
                    text='techniques count', 
                    title='ATT&CK Techniques count per tactic', log_y=False,
                    height=400, color_continuous_scale='Reds')
        
        fig.write_html('./charts/techniques_count_per_tactic.html')

    def chart_defense_techniques_per_tactic(self):
        records = {}
        for tac in self.cfg.tactics_order:
            records.update({
                tac: 0
            })
        
        for dt in self.techniques:
            dtech = self.techniques[dt]
            for tech in dtech.detects:
                tac = self.attack.techniques[tech].tactics[0]
                records[tac] += 1
        
        records_arr = []
        for tac in records:
            records_arr.append({'tactic': tac, 'defense techniques count': records[tac]})
        
        df = DF.from_records(records_arr)
        
        fig = px.bar(df, 
                    x='tactic', y='defense techniques count', 
                    color='defense techniques count', 
                    text='defense techniques count', 
                    title='Defense techniques count per tactic', log_y=False,
                    height=400, color_continuous_scale='Blues')
        
        fig.write_html('./charts/defense_techniques_count_per_tactic.html')

    @staticmethod
    def get_coords(radius, x, y, minresults):
        coords = []
        stepSize = 6.0 # Start from huge parameter to find optimal numner of points arround a circle
        while len(coords) < minresults:
            coords = Defend.get_circle(radius, x, y, stepSize)
            stepSize -= 0.01 # GET DOWN, but gently ;)
        return coords
    
    @staticmethod
    def get_circle(radius, x, y, stepSize=6.0):
        coords = []
        t = 0
        while t < 2 * math.pi:
            coords.append((radius * math.cos(t) + x, radius * math.sin(t) + y))
            t += stepSize
        return coords
    
    @staticmethod
    def find_closest_point(destination, circle, taken):
        closest = None
        closest_val = None
        for pos in circle:
            if pos not in taken:
                dist = math.dist(destination, pos)
                if not closest_val:
                    closest_val = dist
                    closest = pos
                else:
                    if closest_val > dist:
                        closest_val = dist
                        closest = pos
        return closest

    @staticmethod
    def get_square_coordinates(x, y, distance):        
        return [
            [x,y], [x,y+distance], [x+distance, y], [x+distance, y+distance]
        ]

    @staticmethod
    def get_tactics_line_coordinates(x=0, y=0, distance=1000):
        coords = []
        a = 0
        while a < 5:
            tmp = Defend.get_square_coordinates(x, y, distance)
            x = x + distance + distance
            coords.extend(tmp)
            a += 1

        coords.pop(2)  # Space after PRE
        coords.pop(2)  # Space after PRE
        coords.pop(-1) # No need
        coords.pop(-1) # No need
        coords.pop(-5) # Space before high impact tac
        coords.pop(-5) # Space before high impact tac
        return coords