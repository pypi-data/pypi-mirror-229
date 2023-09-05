import pytest
from ..src import wandr

wM = wandr.wandrMain()

def test_typing_type():
    assert type(wM.getTyping("Scyther")) == list
    types = wM.getTyping("Scyther")
    weakness = wM.getWeakness(types, returnType="giveDict")
    assert type(weakness) == dict
    
def test_getWeakness():
    types = wM.getTyping("Scyther")
    weakness = wM.getWeakness(types)
    assert type(weakness) == list
    assert weakness[0] == "Fire"
    assert weakness[3] == "Electric"


def test_getResistance():
    types = wM.getTyping("Bulbasaur")
    resistance = wM.getResistance(types)
    assert type(resistance) == list
    assert resistance[0] == "Water"
    assert resistance[2] == "Grass"



    


