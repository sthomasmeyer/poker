// const BASE_URL = 'http://127.0.0.1:5000';

communityCards = document.getElementById('community-cards');

flopButton = document.getElementById('flop-btn');
turnButton = document.getElementById('turn-btn');
riverButton = document.getElementById('river-btn');
showdownButton = document.getElementById('showdown-btn');

flop = document.getElementById('flop');
turn = document.getElementById('turn');
river = document.getElementById('river');
oppsHand = document.getElementById('opps-hand');

playerScore = document.getElementById('player-score');
oppsScore = document.getElementById('opps-score');

flopButton.onclick = function revealFlop(evt) {
  evt.preventDefault();
  flop.hidden = false;
  flopButton.remove();
  turnButton.hidden = false;
};

turnButton.onclick = function revealTurn(evt) {
  evt.preventDefault();
  turn.hidden = false;
  turnButton.remove();
  riverButton.hidden = false;
};

riverButton.onclick = function revealRiver(evt) {
  evt.preventDefault();
  river.hidden = false;
  riverButton.remove();
  showdownButton.hidden = false;
};

showdownButton.onclick = function showdown(evt) {
  evt.preventDefault();
  showdownButton.remove();
  oppsHand.hidden = false;
  playerScore.hidden = false;
  oppsScore.hidden = false;
};
