"""Data classes for Vatican pope and speech metadata."""

# ----------------------
# :: IMPORTS ::
# ----------------------

from dataclasses import dataclass, field

# ----------------------
# :: CLASSES ::
# ----------------------

@dataclass(frozen=True)
class Speech:
    """Represents an individual text or speech.
    
    Attributes:
        title: The full title of the speech.
        date: Normalized ISO date (YYYY-MM-DD) or None if unknown.
        category: The section or category the speech belongs to.
    """
    title: str
    date: str | None
    category: str

@dataclass
class Pope:
    """Represents a Pope and their associated collection of texts.
    
    Attributes:
        pope_name: The name of the Pope.
        papacy_began: ISO date of the start of the pontificate.
        texts: A list of Speech objects associated with this Pope.
    """
    pope_name: str
    papacy_began: str
    texts: list[Speech] = field(default_factory=list)