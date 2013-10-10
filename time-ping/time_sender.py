import spade
import datetime


class Sender(spade.Agent.Agent):
    """
    Sender class
    """

    class SendTimeBehav(spade.Behaviour.PeriodicBehaviour):
        """
        class for sending current time to client agent
        """

        def onStart(self):
            self.receiver = spade.AID.aid(name='receiver@127.0.0.1', addresses=['xmpp://receiver@127.0.0.1'])

        def _onTick(self):
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setPerformative('inform')
            self.msg.setOntology('time')

            self.msg.addReceiver(self.receiver)
            self.msg.setContent(datetime.datetime.now())

            self.myAgent.send(self.msg)

    def _setup(self):
        print "agent running..."

        behav = self.SendTimeBehav(2)
        self.addBehaviour(behav, None)

if __name__ == '__main__':
    sender = Sender('agent@127.0.0.1', 'secret')
    sender.start()
