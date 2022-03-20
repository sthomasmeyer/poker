// const BASE_URL = 'http://127.0.0.1:5000';

const communityCards = document.getElementById('community-cards');

const flopButton = document.getElementById('flop-btn');
const turnButton = document.getElementById('turn-btn');
const riverButton = document.getElementById('river-btn');

const showdownDiv = document.getElementById('showdown');
const showdownWinButton = document.getElementById('showdown-win-btn');
const showdownLossButton = document.getElementById('showdown-loss-btn');
const showdownWinForm = document.getElementById('showdown-win-form');
const showdownLossForm = document.getElementById('showdown-loss-form');

const flop = document.getElementById('flop');
const turn = document.getElementById('turn');
const river = document.getElementById('river');
const oppsHand = document.getElementById('opps-hand');

const foldButton = document.getElementById('fold-btn');
let callPreFlopButton = document.getElementById('call-pre-flop-btn');

const playerScore = document.getElementById('player-score');
const oppsScore = document.getElementById('opps-score');

callPreFlopButton.onclick = function keepPlaying(evt) {
  evt.preventDefault();
  callPreFlopButton.remove();
  foldButton.hidden = true;
  flopButton.hidden = false;
};

flopButton.onclick = function revealFlop(evt) {
  evt.preventDefault();
  flop.hidden = false;
  flopButton.remove();
  newBtn = document.createElement('button');
  newBtn.setAttribute('id', 'call-post-flop-btn');
  newBtn.innerText = 'Call';
  document.getElementById('options').append(newBtn);
  let callPostFlopButton = document.getElementById('call-post-flop-btn');
  foldButton.hidden = false;

  callPostFlopButton.onclick = function keepPlaying(evt) {
    evt.preventDefault();
    console.log('TEST');
    callPostFlopButton.remove();
    foldButton.hidden = true;
    turnButton.hidden = false;
  };
};

turnButton.onclick = function revealTurn(evt) {
  evt.preventDefault();
  turn.hidden = false;
  turnButton.remove();
  newBtn = document.createElement('button');
  newBtn.setAttribute('id', 'call-post-turn-btn');
  newBtn.innerText = 'Call';
  document.getElementById('options').append(newBtn);
  let callPostTurnButton = document.getElementById('call-post-turn-btn');
  foldButton.hidden = false;

  callPostTurnButton.onclick = function keepPlaying(evt) {
    evt.preventDefault();
    console.log('TESTING...');
    callPostTurnButton.remove();
    foldButton.hidden = true;
    riverButton.hidden = false;
  };
};

riverButton.onclick = function revealRiver(evt) {
  evt.preventDefault();
  river.hidden = false;
  riverButton.remove();
  newBtn = document.createElement('button');
  newBtn.setAttribute('id', 'call-post-river-btn');
  newBtn.innerText = 'Call';
  document.getElementById('options').append(newBtn);
  let callPostRiverButton = document.getElementById('call-post-river-btn');
  foldButton.hidden = false;

  callPostRiverButton.onclick = function finishTheHand(evt) {
    evt.preventDefault();
    console.log('1, 2, 3');
    callPostRiverButton.remove();
    foldButton.hidden = true;
    showdownDiv.hidden = false;
  };
};

if (showdownWinButton != null) {
  showdownWinButton.onclick = function showdown(evt) {
    evt.preventDefault();
    setTimeout(() => {
      showdownWinForm.submit();
    }, 3000);
    showdownWinButton.remove();
    oppsHand.hidden = false;
    playerScore.hidden = false;
    oppsScore.hidden = false;
    setTimeout(() => {
      alert(`
      You've won this hand and $15
      Press 'OK' to see the next hand
      `);
    }, 1000);
  };
}

if (showdownLossButton != null) {
  showdownLossButton.onclick = function showdown(evt) {
    evt.preventDefault();
    setTimeout(() => {
      showdownLossForm.submit();
    }, 3000);
    showdownLossButton.remove();
    oppsHand.hidden = false;
    playerScore.hidden = false;
    oppsScore.hidden = false;
    setTimeout(() => {
      alert(`
      You've lost this hand and $10
      Remember, if you fold before the showdown you only lose $5
      Press 'OK' to see the next hand
      `);
    }, 1000);
  };
}
