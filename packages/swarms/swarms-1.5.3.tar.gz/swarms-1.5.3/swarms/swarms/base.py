from abc import ABC, abstractmethod

class AbstractSwarm(ABC):

    def __init__(self, agents, vectorstore, tools):
        self.agents = agents
        self.vectorstore = vectorstore
        self.tools = tools

    @abstractmethod
    def communicate(self):
        pass

    @abstractmethod
    def run(self):
        pass