
# DEFRA

1. The name DEFRA is a simple shorthand for DEfense FRAmework, thus should be pronouced *dē-fra*. 

2. Directory structure:
```
- DSystems
    - AV.json
    - EDR.json
    - MDE.json
- DTechniques
    - AV
        - Mimikatz-has-been-blocked.json
    - MDE
        - An-anomalous-scheduled-task-was-created.json
- Mitigations
    - Induction-training-for-new-employees.json
- attack.py
- defend.py
- attack.json
- config.json
```

- attack.py - parsing and indexing MITRE ATT&CK data
- defend.py - parsing defense techniques metadata and generating reports
- attack.json - MITRE ATT&CK data
- config.json - all configuration required by attack and defend objects
- Mitigations - all mitigations that are used by the organization, should be represented under this directory.
- DSystems - here defense systems metadata should be placed
- DTechniques - defense techniques, each in separate json file, should be under this directory. They can be additionally divided into subdirectories. 

