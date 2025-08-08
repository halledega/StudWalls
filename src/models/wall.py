from src.models.section import Section

class Wall:
    def __init__(self, stud: Section, stories: dict, length: float):
        self._name = ''
        self.stud = stud
        self.stories = stories
        self.length = length
        self._volume = 0

    @property
    def name(self):
        return f"{self.stud.Plys}-{self.stud.Name}"

    @property
    def volume(self, story: str = ""):
        return self.stud.Area * self.stories[story].height