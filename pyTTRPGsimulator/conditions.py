from .modifiers import Modifier


class Condition(Modifier):
    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f"{self.__class__.__name__}"


class Bleeding(Condition):
    pass


class Blinded(Condition):
    pass


class Burning(Condition):
    pass


class Charmed(Condition):
    pass


class Dazed(Condition):
    pass


class Deafened(Condition):
    pass


class Doomed(Condition):
    pass


class Exhaustion(Condition):
    pass


class Exposed(Condition):
    pass


class Frightened(Condition):
    pass


class Grappled(Condition):
    pass


class Hindered(Condition):
    pass


class Impaired(Condition):
    pass


class Incapacitated(Condition):
    pass


class Intimidated(Condition):
    pass


class Invisible(Condition):
    pass


class Paralyzed(Condition):
    pass


class Petrified(Condition):
    pass


class Poisoned(Condition):
    pass


class Prone(Condition):
    pass


class Rattled(Condition):
    pass


class Restrained(Condition):
    pass


class Slowed(Condition):
    pass


class Stunned(Condition):
    pass


class Surprised(Condition):
    pass


class Taunted(Condition):
    pass


class Unconscious(Condition):
    pass
