from typing import List, Dict, Any, Optional


Action=str
State=Any


class Agent:
  def __init__(self)->None:
    pass
  def update(self, state:State)->Action:
    return Action()


class Monitor:
  def __init__(self)->None:
    self.agents:List[Agent]=[]

  def add_agent(self, a:Agent)->None:
    self.agents.append(a)

  def run(self)->None:
    pass
