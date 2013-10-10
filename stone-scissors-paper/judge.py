import spade


class Judge(spade.Agent.Agent):
    """
    Sender class
    """

    class WaitPlayersBehav(spade.Behaviour.OneShotBehaviour):

        def _process(self):

            self.msg = None
            self.msg = self._receive(True, 1)

            if self.msg and self.msg.getOntology() == 'start_game':
                self.myAgent.players_count += 1
                if self.myAgent.players_count >= 2:
                    self._exitcode = self.myAgent.TRANSLATION_TO_APPROVE
                else:
                    self._exitcode = self.myAgent.TRANSLATION_TO_DEFAULT
            else:
                self._exitcode = self.myAgent.TRANSLATION_TO_DEFAULT

    class GameApproveBehav(spade.Behaviour.OneShotBehaviour):
        """
        class for sending current time to client agent
        """

        def _process(self):

            self.msg = None
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setPerformative('inform')
            self.msg.setOntology('approve_start')

            self.msg.addReceiver(self.myAgent.player_one)
            self.msg.addReceiver(self.myAgent.player_two)
            self.msg.setContent("You can start playing now!")
            self.myAgent.send(self.msg)

            self._exitcode = self.myAgent.TRANSLATION_TO_GAME

    class GameBehav(spade.Behaviour.OneShotBehaviour):

        SERVER = '127.0.0.1'
        WIN = [['rock', 'scissors'], ['paper', 'rock'], ['paper', 'scissors']]

        def evaluate_result(self, player_one, player_two):
            if player_one == player_two:
                return -1
            return [item for item in self.WIN if item[0] == player_one and item[1] == player_two]

        def next_round(self):
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setOntology('next_round')
            self.msg.setContent('Play next round!')
            self.msg.addReceiver(self.myAgent.player_one)
            self.msg.addReceiver(self.myAgent.player_two)

            self.myAgent.send(self.msg)
            self.myAgent.player_one_decision = self.myAgent.player_two_decision = None
            self._exitcode = self.myAgent.TRANSLATION_TO_DEFAULT

        def finish_game(self):
            self._exitcode = self.myAgent.TRANSLATION_TO_END

        def _process(self):

            self.msg = self._receive(True)
            if self.msg and self.msg.getOntology() == 'choice':
                if self.msg.getSender().getName() == 'player_one@{0}'.format(self.SERVER):
                    self.myAgent.player_one_decision = self.msg.content
                else:
                    self.myAgent.player_two_decision = self.msg.content

                if self.myAgent.player_one_decision and self.myAgent.player_two_decision:
                    print 'Player one decision: {0}'.format(self.myAgent.player_one_decision)
                    print 'Player two decision: {0}'.format(self.myAgent.player_two_decision)

                    status = self.evaluate_result(self.myAgent.player_one_decision, self.myAgent.player_two_decision)
                    if status == -1:
                        print 'Remi!'
                        self.next_round()
                    elif status:
                        print 'Player one win round!'
                        self.myAgent.player_one_score += 1
                        if self.myAgent.player_one_score >= 3:
                            print 'Player one WIN GAME!'
                            self.finish_game()
                        else:
                            self.next_round()
                    else:
                        print 'Player two win round!'
                        self.myAgent.player_two_score += 1
                        if self.myAgent.player_two_score >= 3:
                            print 'Player two WIN GAME!'
                            self.finish_game()
                        else:
                            self.next_round()

                    print 'Current result: {0} : {1}'.format(self.myAgent.player_one_score, self.myAgent.player_two_score)
                else:
                    self._exitcode = self.myAgent.TRANSLATION_TO_DEFAULT

    class EndBehav(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            print "END!"
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setOntology('game_end')
            self.msg.setContent('End of game!')

            self.msg.addReceiver(self.myAgent.player_one)
            self.msg.addReceiver(self.myAgent.player_two)
            self.myAgent.send(self.msg)
            self.myAgent._kill()

    def _setup(self):

        self.player_one = spade.AID.aid(name='player_one@127.0.0.1', addresses=['xmpp://player_one@127.0.0.1'])
        self.player_two = spade.AID.aid(name='player_two@127.0.0.1', addresses=['xmpp://player_two@127.0.0.1'])

        self.players_count = 0
        self.player_one_score = 0
        self.player_two_score = 0
        self.player_one_decision = None
        self.player_two_decision = None

        self.STATE_WAIT = 1
        self.STATE_APPROVE = 2
        self.STATE_GAME = 3
        self.STATE_END = 4

        self.TRANSLATION_TO_DEFAULT = 0
        self.TRANSLATION_TO_APPROVE = 10
        self.TRANSLATION_TO_GAME = 20
        self.TRANSLATION_TO_END = 30

        fsm = spade.Behaviour.FSMBehaviour()
        fsm.registerFirstState(self.WaitPlayersBehav(), self.STATE_WAIT)
        fsm.registerState(self.GameApproveBehav(), self.STATE_APPROVE)
        fsm.registerState(self.GameBehav(), self.STATE_GAME)
        fsm.registerLastState(self.EndBehav(), self.STATE_END)

        fsm.registerTransition(self.STATE_WAIT, self.STATE_WAIT, self.TRANSLATION_TO_DEFAULT)
        fsm.registerTransition(self.STATE_WAIT, self.STATE_APPROVE, self.TRANSLATION_TO_APPROVE)

        fsm.registerTransition(self.STATE_APPROVE, self.STATE_APPROVE, self.TRANSLATION_TO_DEFAULT)
        fsm.registerTransition(self.STATE_APPROVE, self.STATE_GAME, self.TRANSLATION_TO_GAME)

        fsm.registerTransition(self.STATE_GAME, self.STATE_GAME, self.TRANSLATION_TO_DEFAULT)
        fsm.registerTransition(self.STATE_GAME, self.STATE_END, self.TRANSLATION_TO_END)

        self.setDefaultBehaviour(fsm)

if __name__ == '__main__':
    sender = Judge('judge@127.0.0.1', 'secret')
    #sender.setDebugToScreen()
    sender.start()
