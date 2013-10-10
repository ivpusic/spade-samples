import spade


class Receiver(spade.Agent.Agent):

    class ReceiveTimeBehav(spade.Behaviour.Behaviour):
        """behaviour receives messages from time ontology"""

        def _process(self):
            self.msg = None
            self.msg = self._receive(True, 10)

            if self.msg:
                print "got a message from time ontology!! Content: {0}".format(self.msg.content)
            else:
                print "no message received from time ontology!"

    def _setup(self):
        print "starting agent..."

        time_template = spade.Behaviour.ACLTemplate()
        time_template.setOntology('time')
        tmt = spade.Behaviour.MessageTemplate(time_template)

        rtb = self.ReceiveTimeBehav()
        self.addBehaviour(rtb, tmt)


if __name__ == '__main__':
    receiver = Receiver('receiver@127.0.0.1', 'secret')
    receiver.start()
