from dataclasses import dataclass


@dataclass
class Settings:
    camera_index: int = 0
    debug: bool = True
