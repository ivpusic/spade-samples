import spade
from random import choice


class Player(spade.Agent.Agent):
    """
    player which represents player
    """

    class StartGameBehav(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setPerformative('inform')
            self.msg.setOntology('start_game')
            self.msg.setContent('I am ready to start playing')
            self.msg.addReceiver(self.myAgent.judge)

            self.myAgent.send(self.msg)
            self._exitcode = self.myAgent.TRANSLATION_TO_WAIT

    class WaitForGameBehav(spade.Behaviour.OneShotBehaviour):

        def _process(self):

            self.msg = None
            self.msg = self._receive(True)

            if self.msg and self.msg.getOntology() == 'approve_start':
                self._exitcode = self.myAgent.TRANSLATION_TO_GAME
            else:
                self._exitcode = self.myAgent.TRANSLATION_TO_DEFAULT

    class GameBehav(spade.Behaviour.OneShotBehaviour):

        def gen_and_send_decision(self):

            decision = choice(self.myAgent.items)
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setOntology('choice')
            self.msg.setContent(decision)

            self.msg.addReceiver(self.myAgent.judge)
            self.myAgent.send(self.msg)

        def _process(self):
            self.response = None
            self.response = self._receive(True)

            if self.response and self.response.getOntology() == 'game_end':
                self._exitcode = self.myAgent.TRANSLATION_TO_FINISH
            else:
                self.gen_and_send_decision()
                self._exitcode = self.myAgent.TRANSLATION_TO_DEFAULT

    class EndGameBehav(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            print "player exit..."
            self.myAgent._kill()

    def _setup(self):

        print "starting player..."

        self.judge = spade.AID.aid(name='judge@127.0.0.1', addresses=['xmpp://judge@127.0.0.1'])
        self.items = ['rock', 'paper', 'scissors']

        self.STATE_START = 1
        self.STATE_WAIT = 2
        self.STATE_GAME = 3
        self.STATE_WINNER = 4

        self.TRANSLATION_TO_DEFAULT = 0
        self.TRANSLATION_TO_START = 10
        self.TRANSLATION_TO_WAIT = 20
        self.TRANSLATION_TO_GAME = 30
        self.TRANSLATION_TO_FINISH = 40

        fsm = spade.Behaviour.FSMBehaviour()
        fsm.registerFirstState(self.StartGameBehav(), self.STATE_START)
        fsm.registerState(self.WaitForGameBehav(), self.STATE_WAIT)
        fsm.registerState(self.GameBehav(), self.STATE_GAME)
        fsm.registerLastState(self.EndGameBehav(), self.STATE_WINNER)

        fsm.registerTransition(self.STATE_START, self.STATE_START, self.TRANSLATION_TO_DEFAULT)
        fsm.registerTransition(self.STATE_START, self.STATE_WAIT, self.TRANSLATION_TO_WAIT)

        fsm.registerTransition(self.STATE_WAIT, self.STATE_WAIT, self.TRANSLATION_TO_DEFAULT)
        fsm.registerTransition(self.STATE_WAIT, self.STATE_GAME, self.TRANSLATION_TO_GAME)

        fsm.registerTransition(self.STATE_GAME, self.STATE_GAME, self.TRANSLATION_TO_DEFAULT)
        fsm.registerTransition(self.STATE_GAME, self.STATE_WINNER, self.TRANSLATION_TO_FINISH)

        self.setDefaultBehaviour(fsm)


if __name__ == '__main__':
    player_one = Player('player_one@127.0.0.1', 'secret')
    player_two = Player('player_two@127.0.0.1', 'secret')

    player_one.start()
    player_two.start()
