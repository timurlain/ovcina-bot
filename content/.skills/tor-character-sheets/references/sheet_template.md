# Hero Data Structure

Each hero dict must contain these fields:

```python
hero = {
    'name': 'Full Czech Name',
    'player': 'Player Name (age)',
    'culture': 'e.g. Hobbit z Hurecka',
    'calling': 'Czech calling name',
    'age': 'e.g. 14-15',
    'shadow': 'Shadow path in Czech',

    # Attributes: list of (name, value, target_number)
    'attrs': [
        ('SILA', 3, 17),
        ('SRDCE', 6, 14),
        ('DUVTIP', 5, 15),
    ],

    # Derived values: list of (label, value_string)
    'derived': [
        ('Vydrz', '23'),
        ('Nadeje', '16'),
        ('Odrazeni', '15'),
        ('Udatnost / Moudrost', '1 / 1'),
        ('Zatez', '0'),
    ],

    # Skills: 3 groups, each with (group_title, [(name, rating, is_favoured)])
    # Group titles include attribute name and TN: "SILA  CC 17"
    'skill_groups': [
        ('SILA  CC 17', [
            ('Pusobivost', 0, False),
            ('Mrstnost', 1, False),
            # ... 6 skills per group
        ]),
        ('SRDCE  CC 14', [...]),
        ('DUVTIP  CC 15', [...]),
    ],

    # Combat proficiencies: list of (name, rating)
    'combat': [
        ('Rvacka', 1),
        ('Mece', 0),
    ],

    # Weapons: list of description strings
    'weapons': [
        'Kratky nuz -- Poskoz. 2, Nebezp. 14, Zatez 0',
    ],

    # Useful items with bonuses
    'items': [
        'Pistalka na ptaky -> HUDBA +1k',
    ],

    # Keywords and special items
    'keywords': [...],

    # Relationships and notes
    'notes': [...],

    # XP earned lines
    'xp_earned': [
        'Ep 1 -- ...: 3 dovednostnich + 3 dobrodruznych bodu',
        'CELKEM: ...',
    ],

    'total_sp': 9,  # Total skill points available
    'total_ap': 9,  # Total adventure points available

    # Recommendations for spending
    'sp_recs': ['Povzbuzovani 2->3 (3 body)'],
    'ap_recs': ['Moudrost 1->2 (~8 bodu) -> ctnost'],

    # Story paragraphs (list of strings, empty string = paragraph break)
    'story': [
        'First paragraph of backstory...',
        'Second paragraph...',
    ],
}
```

## XP Cost Tables (hardcoded in generator)

### Skill Points
| From | To | Cost |
|------|-----|------|
| 0 | 1 | 1 SP |
| 1 | 2 | 2 SP |
| 2 | 3 | 3 SP |
| 3 | 4 | 5 SP |

Max 1 rank per skill per Fellowship Phase.

### Adventure Points
| Type | Cost |
|------|------|
| Combat prof 0->1 | 2 AP |
| Combat prof 1->2 | 4 AP |
| Combat prof 2->3 | 6 AP |
| New Valour rank | -> Reward |
| New Wisdom rank | -> Virtue |

Only Valour OR Wisdom per Fellowship Phase.

## Hobbit Virtues (hardcoded)
- Houzevnaty jako koren stromu
- Maly clovicek
- Presna muska
- Tri delaji spolecnost
- Umeni zmizet
- V nouzi hrdinou
