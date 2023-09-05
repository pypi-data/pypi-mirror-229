# WANDR (Weakness and Resistance Tool)

WANDR is a prerequisite for autoLocke, but is also available for use by others.
WANDR can take any pokemon as input, and return it's types, weaknesses and resistances
in dictionary or list format.

### How to Install

**pip install wandr**


### Usage
'''
import wandr as wM

types = wM.getTyping(pokemon="Charmander")
'''
Returns:

**['Fire']**

You can also get any type's resistance.
'''
resistance = wM.getResistance(typeList=types, returnType="giveList")
'''
This would return

**['Fire', 'Grass', 'Ice', 'Bug', 'Steel']**

Any duplicate weaknesses (4x) or duplicate resistances (0.25x) will be returned twice in the list.

### Further Usage

You can also get a resistance/weakness pandas dataframe.
'''
import wandr as wM

types = wM.getTyping("Scyther")
weakness = wM.getWeakness(typeList=types, returnType="giveDict")

'''


The output would be 

'''
{'Ground': 0, 'Fire': 2, 'Water': 0, 'Grass': 0, 'Ice': 2, 'Electric': 2, 'Rock': 4, 'Flying': 2, 'Normal': 0, 'Fighting': 0, 'Poison': 0, 'Psychic': 0, 'Bug': 0, 'Ghost': 0, 'Dragon': 0, 'Steel': 0, 'Dark': 0}
'''

Since scyther has a double weakness to Rock, it is returned in the dictionary as 4.

### Issues

Please direct any issues to the github issues tab.