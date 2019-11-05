from dataclasses import dataclass


@dataclass
class Identifier:
    # Data class that holds all the subject identifier, wave number, task name, and run number,
    # because this information gets passed around a lot to create the correct file names or data structures
    subject_id: str = ''
    wave: str = ''
    task: str = ''
    run: str = ''
