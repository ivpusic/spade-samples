import spade
from chatterbotapi import ChatterBotFactory, ChatterBotType


class ChatBot(spade.Agent.Agent):

    def __init__(self, ip, _pass, sendF):
        spade.Agent.Agent.__init__(self, ip, _pass)
        self.sendFirst = sendF

    def send_msg(self, content):
        msg = spade.ACLMessage.ACLMessage()
        msg.setPerformative("inform")
        msg.addReceiver(spade.AID.aid("a@127.0.0.1", ["xmpp://a@127.0.0.1"]))

        botsession = self.bot.create_session()
        s = botsession.think(content)

        msg.setContent(s)
        msg.setLanguage('english')

        self.send(msg)

    class InitChatBot(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.send_msg("")

    class MessageManager(spade.Behaviour.EventBehaviour):
        def _process(self):
            msg = self._receive().getContent()
            print msg
            self.myAgent.send_msg(msg)

    def _setup(self):

        factory = ChatterBotFactory()
        self.bot = factory.create(ChatterBotType.CLEVERBOT)
        self.template = spade.Behaviour.ACLTemplate()
        self.template.setLanguage('english')
        self.t = spade.Behaviour.MessageTemplate(self.template)

        self.addBehaviour(self.MessageManager(), self.t)
        if self.sendFirst:
            self.addBehaviour(self.InitChatBot())

if __name__ == '__main__':
    a = ChatBot('a@127.0.0.1', 'secret', True)
    b = ChatBot('b@127.0.0.1', 'secret', False)

    a.start()
    b.start()
