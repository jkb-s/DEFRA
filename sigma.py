import yaml
from dataclasses import dataclass, field
from os import walk, path

@dataclass
class SigmaRule:
    title: str
    id: str = ""
    severity: str = ""
    techniques: list = field(default_factory=list)
    status: str = ""
    author: str = ""
    
class Sigma:

    def __init__(self, rootpath='./sigma/rules/windows/'):
        
        rules = []
        for root, subdirectories, files in walk(rootpath):
            for file in files:
                if file[-4:] == ".yml":
                    filename = path.join(root, file)
                    with open(filename, 'r', encoding='utf-8') as fobj:
                        data = yaml.safe_load(fobj)
                        fobj.close()

                        rules.append(data)
        
        self.rules = []
        self.rules_no_mapping = []

        for rule in rules:
            techniques = []
            for ele in rule.get('tags', []):
                if 't1' in ele:
                    techniques.append(ele.replace('attack.', '').title())
        
            sig = SigmaRule(
                    title = rule['title'], 
                    severity = rule['level'], 
                    id = rule['id'], 
                    status = rule['status'],
                    author = rule['author'],
                    techniques = techniques
            )
            if techniques:
                self.rules.append(sig)
            else:
                self.rules_no_mapping.append(sig)

        
