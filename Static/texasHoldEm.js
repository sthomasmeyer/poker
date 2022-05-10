/* SECTION [0]: ESTABLISHING KEY VARIABLES */

// The following HTML elements are *always* generated...
// at the beginning of a hand, and they are revealed to...
// users when appropriate.
const revealFlopButton = document.getElementById('reveal-flop-btn');
const revealTurnButton = document.getElementById('reveal-turn-btn');
const revealRiverButton = document.getElementById('reveal-river-btn');

// The following variables capture elements related to...
// the active-user.
const userChipCount = document.getElementById('user-chip-count');
const userCommitedChips = document.getElementById('user-commited');
const userBlind = document.getElementById('user-blind');
const userScore = document.getElementById('user-score');
const userOptions = document.getElementById('user-options');

// The following [foldButton] variable is aligned to...
// the player's ever-present option to fold.
const foldButton = document.getElementById('fold-btn');

const allocatorContainer = document.getElementById('allocator-container');
const allocator = document.getElementById('allocator');
const allocatorValue = document.getElementById('allocator-val');
const allocatorSubmitButton = document.getElementById('allocator-submit-btn');

// The following variables capture elements related to...
// the community cards (+) the pot.
const communityCards = document.getElementById('community-cards');
const pot = document.getElementById('pot');

// The following variables capture elements related to...
// the ai-opponent.
const oppHand = document.getElementById('ai-opp-hand');
const oppChipCount = document.getElementById('ai-opp-chip-count');
const oppCommitedChips = document.getElementById('ai-opp-commited');
const oppBlind = document.getElementById('ai-opp-blind');
const oppScore = document.getElementById('ai-opp-score');

// The following "counter" variables are designed to track...
// the number of bets / raises in a given betting round.
let preFlopRaiseCounter = 0;
let postFlopRaiseCounter = 0;
let postTurnRaiseCounter = 0;
let postRiverRaiseCounter = 0;

/* SECTION [1]: VITAL FUNCTIONS */

async function updatePot() {
  try {
    const res = await axios.get('/texas_hold_em/update/pot');
    console.log(`Updated Pot Val: ${res.data}`);
    // Remove the DOM-element associated w/ the...
    // value of the pot:
    pot.removeChild(pot.children[1]);
    // Replace it with the updated value.
    let updatePot = document.createElement('td');
    updatePot.innerText = res.data;
    pot.append(updatePot);
  } catch (error) {
    console.log(error);
  }
}

async function updateUserStack() {
  try {
    const res = await axios.get('/texas_hold_em/update/user_chip_count');
    console.log(`Updated User Stack: ${res.data}`);
    // Remove the DOM-element associated w/ the...
    // initial value of the user's stack:
    userChipCount.children[1].remove();
    // Replace it with the updated value.
    let updateUserStack = document.createElement('td');
    updateUserStack.innerText = res.data;
    userChipCount.append(updateUserStack);
  } catch (error) {
    console.log(error);
  }
}

async function updateOppStack() {
  try {
    const res = await axios.get('/texas_hold_em/update/ai_opp_chip_count');
    console.log(`Updated Opp Stack: ${res.data}`);
    // Remove the DOM-element associated w/ the...
    // initial value of the ai-opp's stack:
    oppChipCount.children[1].remove();
    // Replace it with the updated value:
    let updateOppStack = document.createElement('td');
    updateOppStack.innerText = res.data;
    oppChipCount.append(updateOppStack);
  } catch (error) {
    console.log(error);
  }
}

async function getOppCards() {
  try {
    const res = await axios.get('/texas_hold_em/ai_opp_cards');
    console.log(`Opp Hand: ${res.data}`);
    const computerHand = [];
    res.data.forEach((element) =>
      computerHand.push(element.join().replace(',', ''))
    );
    console.log(computerHand);
    displayHand = document.createElement('td');
    let i = 0;
    for (i = 0; i < computerHand.length; i++) {
      displayHand.innerText += `${computerHand[i]} `;
    }
    oppHand.append(displayHand);
  } catch (error) {
    console.log(error);
  }
}

async function getScore(path, anchor) {
  try {
    const res = await axios.get(path);
    displayScore = document.createElement('td');
    displayScore.innerText = res.data;
    anchor.append(displayScore);
  } catch (error) {
    console.log(error);
  }
}

function updateCommitedChips(anchor, val) {
  // Remove the DOM-element associated w/ the...
  // initial value of player's commited chips.
  anchor.children[1].remove();
  // Replace it with the updated value.
  let updatedVal = document.createElement('td');
  updatedVal.innerText = val;
  anchor.append(updatedVal);
}

function generateCheckButton(path) {
  let checkButton = document.createElement('button');
  checkButton.innerText = 'Check';
  userOptions.append(checkButton);

  checkButton.onclick = function userAction(evt) {
    evt.preventDefault();

    userCheck();
    checkButton.remove();
    if (path.includes('pre_flop')) {
      revealFlopButton.hidden = false;
    } else if (path.includes('post_flop')) {
      revealTurnButton.hidden = false;
    } else if (path.includes('post_turn')) {
      revealRiverButton.hidden = false;
    } else if (path.includes('post_river')) {
      generateShowdownButton();
    }

    async function userCheck() {
      try {
        const res = await axios.get(path);
        console.log(`[CHECK] User Chips Commited: ${res.data}`);
      } catch (error) {
        console.log(error);
      }
    }
  };
}

function generateCallButton(path) {
  let callButton = document.createElement('button');
  callButton.innerText = 'Call';
  userOptions.append(callButton);
  foldButton.hidden = false;

  callButton.onclick = function userAction(evt) {
    evt.preventDefault();

    userCall();
    callButton.remove();
    foldButton.hidden = true;
    if (path.includes('pre_flop')) {
      revealFlopButton.hidden = false;
    } else if (path.includes('post_flop')) {
      revealTurnButton.hidden = false;
    } else if (path.includes('post_turn')) {
      revealRiverButton.hidden = false;
    } else if (path.includes('post_river')) {
      generateShowdownButton();
    }

    async function userCall() {
      try {
        const res = await axios.get(path);

        totalCommitedChips =
          Number(userCommitedChips.children[1].innerText) + res.data;

        if (path.includes('pre_flop')) {
          updateCommitedChips(userCommitedChips, res.data);
        } else {
          updateCommitedChips(userCommitedChips, totalCommitedChips);
        }

        updatePot();
        updateUserStack();
      } catch (error) {
        console.log(error);
      }
    }
  };
}

class Bet {
  constructor(container, slider, val, min, max, button) {
    this.container = container;
    this.slider = slider;
    this.val = val;
    this.min = min;
    this.max = max;
    this.button = button;
  }

  revealKeyElements = () => (this.container.hidden = false);
  setMinBet = () => this.slider.setAttribute('min', this.min);
  setMaxBet = () => this.slider.setAttribute('max', this.max);
  setDefaultValue = () => this.slider.setAttribute('value', this.min);
  activateDisplay = () => (this.val.innerText = `[${this.slider.value}]`);
  responsiveAllocator() {
    this.slider.oninput = () => (this.val.innerHTML = `[${this.slider.value}]`);
  }
  functionalButton() {
    this.button.onclick = (evt) => {
      evt.preventDefault();
      console.log(`Raise: ${this.slider.value}`);
    };
  }
}

function generateShowdownButton() {
  let showdownContainer = document.createElement('td');

  let showdownForm = document.createElement('form');
  showdownForm.setAttribute('action', '/texas_hold_em/showdown');

  let showdownButton = document.createElement('button');
  showdownButton.innerText = 'Showdown';
  showdownButton.onclick = function showdown(evt) {
    evt.preventDefault();
    setTimeout(() => {
      showdownForm.submit();
    }, 1000);
    showdownButton.remove();

    getOppCards();
    getScore('/texas_hold_em/user_score', userScore);
    getScore('/texas_hold_em/computer_opp_score', oppScore);

    setTimeout(() => {
      alert(`
      Press 'OK' to see the next hand
      `);
    }, 500);
  };

  showdownForm.append(showdownButton);
  showdownContainer.append(showdownForm);
  userOptions.append(showdownContainer);
}

/* SECTION [2]: PRE-FLOP ACTION */

// This [action()] function is triggered "onload"...
window.onload = function action() {
  console.log(`User (blind) Chips Commited: ${userBlind.innerText}`);
  console.log(`AI (blind) Chips Commited: ${oppBlind.innerText}`);

  // If the ai-opp is playing from the small-blind position...
  // then they will be the first player to act.
  if (userBlind.innerText > oppBlind.innerText) {
    console.log('The action is on Cortana.');

    // This asynchronous function makes a GET request...
    // one of this application's "hidden" URLs that...
    // triggers the ai-opp's decision making process.
    async function cortanaPreFlopDecision() {
      try {
        const res = await axios.get('/texas_hold_em/ai_pre_flop_decision');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        // If the GET request produces anything other than...
        // a number, specifically the number of chips...
        // that the ai-opp has decided to bet. Then they...
        // have chosen to fold this hand.
        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        console.log(`AI Chips Commited: ${res.data}`);

        // Update the value associated w/ the number of...
        // chips the ai-opp has commited.
        updateCommitedChips(oppCommitedChips, res.data);

        // Execute [updatePot()] + [updateOppStack()] functions.
        updatePot();
        updateOppStack();

        if (oppCommitedChips.children[1].innerText == userBlind.innerText) {
          console.log('Cortana decided to call.');
          // If Cortana calls, then the active-user can check or bet.

          generateCheckButton('/texas_hold_em/user_pre_flop_check');
          foldButton.hidden = true;

          let preFlopRaise = new Bet(
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          preFlopRaise.revealKeyElements();
          preFlopRaise.setMinBet();
          preFlopRaise.setMaxBet();
          preFlopRaise.setDefaultValue();
          preFlopRaise.activateDisplay();
          preFlopRaise.responsiveAllocator();
          preFlopRaise.functionalButton();
        } else if (
          oppCommitedChips.children[1].innerText > userBlind.innerText
        ) {
          console.log('Cortana decided to raise.');

          preFlopRaiseCounter += 1;
          console.log(`Pre-flop Raise Count: ${preFlopRaiseCounter}`);

          generateCallButton('/texas_hold_em/user_pre_flop_call');
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPreFlopDecision();
  } else {
    console.log('The action is on the active user.');
    generateCallButton('/texas_hold_em/user_pre_flop_call');
  }
};

/* SECTION [3]: POST-FLOP ACTION */

revealFlopButton.onclick = function revealFlop(evt) {
  evt.preventDefault();

  // Execute the asynchronous [getFlop()] function.
  getFlop();

  // Delete this button, it is no longer necessary.
  revealFlopButton.remove();

  // Capture flop data from the db (+) display it.
  async function getFlop() {
    try {
      const res = await axios.get('/texas_hold_em/flop');
      console.log(`FLOP: ${res.data}`);
      const flop = [];
      res.data.forEach((element) => flop.push(element.join().replace(',', '')));
      console.log(flop);
      displayFlop = document.createElement('td');
      let i = 0;
      for (i = 0; i < flop.length; i++) {
        displayFlop.innerText += `${flop[i]} `;
      }
      communityCards.append(displayFlop);
    } catch (error) {
      console.log(error);
    }
  }

  // If the active-user is the dealer, then the ai-opp...
  // will be the first to act after the flop is revealed.
  if (document.getElementById('user-name').innerText.includes('dealer')) {
    console.log('The action is on Cortana.');

    // This asynchronous function makes a GET request...
    // one of this application's "hidden" URLs that...
    // triggers the ai-opp's decision making process.
    async function cortanaPostFlopDecision() {
      try {
        const res = await axios.get('/texas_hold_em/ai_post_flop_decision');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        // If the GET request produces anything other than...
        // a number, specifically the number of chips...
        // that the ai-opp has decided to bet. Then they...
        // have chosen to fold this hand.
        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        // At this point in the hand, the total number of chips...
        // the ai-opp has commited is the sum of their pre-flop...
        // commitment (oppCommitedChips.children[1].innerText)...
        // and the result (res.data) of this GET request.
        totalCommitedChips =
          Number(oppCommitedChips.children[1].innerText) + res.data;
        console.log(`Post-flop AI Chips Commited: 
        ${oppCommitedChips.children[1].innerText} + ${res.data} = ${totalCommitedChips}`);

        // Update the value associated w/ the number of...
        // chips the ai-opp has commited.
        updateCommitedChips(oppCommitedChips, totalCommitedChips);
        // Execute [updatePot()] + [updateOppStack()] functions.
        updatePot();
        updateOppStack();

        // This [if]-statement is designed to check whether...
        // or not the ai-opp has checked.
        if (
          oppCommitedChips.children[1].innerText ==
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');
          generateCheckButton('/texas_hold_em/user_post_flop_check');
        } else if (
          oppCommitedChips.children[1].innerText >
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postFlopRaiseCounter += 1;
          console.log(`Post-flop Raise Count: ${postFlopRaiseCounter}`);
          generateCallButton('/texas_hold_em/user_post_flop_call');
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPostFlopDecision();
  } else {
    console.log('The action is on the active user.');
    generateCheckButton('/texas_hold_em/user_post_flop_check');
  }
};

/* SECTION [4]: POST-TURN ACTION */

revealTurnButton.onclick = function revealTurn(evt) {
  evt.preventDefault();

  revealTurnButton.remove();
  getTurn();

  async function getTurn() {
    try {
      const res = await axios.get('/texas_hold_em/turn');
      console.log(`TURN: ${res.data}`);
      const turn = [];
      res.data.forEach((element) => turn.push(element.join().replace(',', '')));
      displayTurn = document.createElement('td');
      displayTurn.innerText = `${turn} `;
      communityCards.append(displayTurn);
    } catch (error) {
      console.log(error);
    }
  }

  if (document.getElementById('user-name').innerText.includes('dealer')) {
    console.log('The action is on Cortana.');

    async function cortanaPostTurnDecision() {
      try {
        const res = await axios.get('/texas_hold_em/ai_post_turn_decision');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        totalCommitedChips =
          Number(oppCommitedChips.children[1].innerText) + res.data;
        console.log(`Post-turn AI Chips Commited: 
        ${oppCommitedChips.children[1].innerText} + ${res.data} = ${totalCommitedChips}`);

        updateCommitedChips(oppCommitedChips, totalCommitedChips);
        updatePot();
        updateOppStack();

        if (
          oppCommitedChips.children[1].innerText ==
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');

          generateCheckButton('/texas_hold_em/user_post_turn_check');
        } else if (
          oppCommitedChips.children[1].innerText >
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postTurnRaiseCounter += 1;
          console.log(`Post-turn Raise Count: ${postTurnRaiseCounter}`);

          generateCallButton('/texas_hold_em/user_post_turn_call');
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPostTurnDecision();
  } else {
    console.log('The action is on the active user.');
    generateCheckButton('/texas_hold_em/user_post_turn_check');
  }
};

/* SECTION [5]: POST-RIVER ACTION */

revealRiverButton.onclick = function revealRiver(evt) {
  evt.preventDefault();

  revealRiverButton.remove();
  getRiver();

  async function getRiver() {
    try {
      const res = await axios.get('/texas_hold_em/river');
      console.log(`RIVER: ${res.data}`);
      const river = [];
      res.data.forEach((element) =>
        river.push(element.join().replace(',', ''))
      );
      displayRiver = document.createElement('td');
      displayRiver.innerText = river;
      communityCards.append(displayRiver);
    } catch (error) {
      console.log(error);
    }
  }

  if (document.getElementById('user-name').innerText.includes('dealer')) {
    console.log('The action is on Cortana.');

    async function cortanaPostRiverDecision() {
      try {
        const res = await axios.get('/texas_hold_em/ai_post_river_decision');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        totalCommitedChips =
          Number(oppCommitedChips.children[1].innerText) + res.data;
        console.log(`Post-river AI Chips Commited: 
        ${oppCommitedChips.children[1].innerText} + ${res.data} = ${totalCommitedChips}`);

        updateCommitedChips(oppCommitedChips, totalCommitedChips);
        updatePot();
        updateOppStack();

        if (
          oppCommitedChips.children[1].innerText >
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postRiverRaiseCounter += 1;
          console.log(`Post-river Raise Count: ${postRiverRaiseCounter}`);

          generateCallButton('/texas_hold_em/user_post_river_call');
        } else if (
          oppCommitedChips.children[1].innerText ==
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');

          generateCheckButton('/texas_hold_em/user_post_river_check');
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPostRiverDecision();
  } else {
    console.log('The action is on the active user.');
    generateCheckButton('/texas_hold_em/user_post_river_check');
  }
};
