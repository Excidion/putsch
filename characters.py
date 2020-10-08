from actions import Income, ForeignAid, Tax, Coup, Assassinate, Steal, Exchange
from utils import RandomNameGenerator


class BaseCharacter:
    def __init__(self, name=None):
        self.name = RandomNameGenerator().get_random_name() if name is None else name
        self.revealed = False
        self.actions = {
            Income,
            ForeignAid,
            Coup,
        }
        self.blocks = set()

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self):
        title = self.__class__.__name__ if self.revealed else "Influence"
        if self.name is None:
            return f"An anonymous {title}"
        else:
            return f"{title} {self.name}"

    def reveal(self):
        assert self.revealed == False, f"{self} is already revealed."
        self.revealed = True
        print(f"{self} was revealed.")
        return type(self)


class Ambassador(BaseCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions.add(Exchange)
        self.blocks.add(Steal)


class Assassin(BaseCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions.add(Assassinate)


class Captain(BaseCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions.add(Steal)
        self.blocks.add(Steal)


class Contessa(BaseCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocks.add(Assassinate)


class Duke(BaseCharacter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions.add(Tax)
        self.blocks.add(ForeignAid)
