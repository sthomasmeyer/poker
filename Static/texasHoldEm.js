/* SECTION [0]: ESTABLISHING KEY VARIABLES */

// The following HTML elements are *always* generated at the...
// beginning of a hand, and revealed to users when appropriate.
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

// The following HTML elements are aligned to the active-user betting...
// system. They are generated at the beginning of each hand, and...
// revealed to users when appropriate.
const allocatorContainer = document.getElementById('allocator-container');
const allocatorForm = document.getElementById('allocator-form');
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

    if (res.data === 135) {
      displayScore.innerText = `ROYAL FLUSH --> ${res.data} points`;
    } else if (res.data < 135 && res.data > 120) {
      displayScore.innerText = `STRAIGHT FLUSH --> ${res.data} points`;
    } else if (res.data < 120 && res.data > 105) {
      displayScore.innderText = `QUADS --> ${res.data} points`;
    } else if (res.data < 105 && res.data > 90) {
      displayScore.innerText = `FULL HOUSE --> ${res.data} points`;
    } else if (res.data < 90 && res.data > 75) {
      displayScore.innderText = `FLUSH --> ${res.data} points`;
    } else if (res.data < 75 && res.data > 60) {
      displayScore.innerText = `STRAIGHT --> ${res.data} points`;
    } else if (res.data < 60 && res.data > 45) {
      displayScore.innerText = `THREE-OF-A-KIND --> ${res.data} points`;
    } else if (res.data < 45 && res.data > 30) {
      displayScore.innerText = `TWO-PAIR --> ${res.data} points`;
    } else if (res.data < 30 && res.data > 15) {
      displayScore.innerText = `PAIR --> ${res.data} points`;
    } else if (res.data < 15) {
      displayScore.innerText = `HIGH-CARD --> ${res.data} points`;
    }

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
  // Generate the "CHECK" button (+) append it to [userOptions].
  let checkButton = document.createElement('button');
  checkButton.innerText = 'Check';
  checkButton.setAttribute('id', 'check-btn');
  userOptions.append(checkButton);

  checkButton.onclick = function userAction(evt) {
    evt.preventDefault();

    // Execute the asynchronous [userCheck()] function.
    userCheck();
    // Remove this "CHECK" button.
    checkButton.remove();
    // Hide the HTML elements associated w/ the user-betting system.
    allocatorContainer.hidden = true;
    // The following [if]-statements ensure that the appropriate button...
    // is revealed after the active-user chooses to CHECK.
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
  // Generate the "CALL" button (+) append to [userOptions].
  let callButton = document.createElement('button');
  callButton.innerText = 'Call';
  callButton.setAttribute('id', 'call-btn');
  userOptions.append(callButton);

  // If the active-user has the option to call, then they have the...
  // option to fold. Reveal the "FOLD" button.
  foldButton.hidden = false;

  callButton.onclick = function userAction(evt) {
    evt.preventDefault();

    // Execute the asynchronous [userCall()] function.
    userCall();
    // Remove this "CALL" button.
    callButton.remove();
    // Hide the HTML elements associated w/ the user-betting system (+) the "FOLD" button.
    allocatorContainer.hidden = true;
    foldButton.hidden = true;
    // The following [if]-statements ensure that the appropriate button...
    // is revealed after the active-user chooses to CALL.
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

        updateCommitedChips(userCommitedChips, res.data);
        updatePot();
        updateUserStack();
      } catch (error) {
        console.log(error);
      }
    }
  };
}

function generateShowdownButton() {
  let showdownContainer = document.createElement('td');

  let showdownForm = document.createElement('form');
  showdownForm.setAttribute('action', '/texas_hold_em/showdown');

  let showdownButton = document.createElement('button');
  showdownButton.innerText = 'Showdown';
  showdownButton.setAttribute('id', 'showdown-btn');

  showdownButton.onclick = function showdown(evt) {
    evt.preventDefault();
    showdownButton.remove();

    // Execute the following functions to reveal...
    // the opp's cards, their score, and the user's score.
    getOppCards();
    getScore('/texas_hold_em/user_score', userScore);
    getScore('/texas_hold_em/computer_opp_score', oppScore);

    let nextHandButton = document.createElement('button');
    nextHandButton.innerText = 'Deal the Next Hand';
    nextHandButton.setAttribute('id', 'next-hand-btn');

    // Append the [nextHandButton] to [userOptions].
    userOptions.append(nextHandButton);

    // The [nextHandButton] 'onClick' function should...
    // submit the [showdownForm].
    nextHandButton.onclick = function dealNext(evt) {
      // Remove this button.
      nextHandButton.remove();
      // Submit the form.
      showdownForm.submit();
    };
  };

  showdownForm.append(showdownButton);
  showdownContainer.append(showdownForm);
  userOptions.append(showdownContainer);
}

/* SECTION [2]: THE 'BET' CLASS */

class Bet {
  constructor(
    bettingRound,
    parentElement,
    rangeSlider,
    inputDisplay,
    minBet,
    maxBet,
    submitButton
  ) {
    // The [bettingRound] attribute will be:
    // "pre_flop", "post_flop", "post_turn", or "post_river"
    // Note, this attribute will operate as a query parameter.
    this.bettingRound = bettingRound;
    // The [parentElement] is the HTML element that...
    // contains the user-betting system.
    this.parentElement = parentElement;
    // The [rangeSlider] is a unique HTML-input type that allows...
    // users to manually select a value w/ a sliding mechanism.
    this.rangeSlider = rangeSlider;
    // The [inputDisplay] is an HTML 'label' element that...
    // will be updated dynamically based on user-actions.
    this.inputDisplay = inputDisplay;
    this.minBet = minBet;
    this.maxBet = maxBet;
    this.submitButton = submitButton;
  }

  revealUserBettingMechanism = () => (this.parentElement.hidden = false);
  setMinBet = () => this.rangeSlider.setAttribute('min', this.minBet);
  setMaxBet = () => this.rangeSlider.setAttribute('max', this.maxBet);
  setDefaultInputVal = () =>
    this.rangeSlider.setAttribute('value', this.minBet);
  activateDisplay = () => {
    this.inputDisplay.innerHTML = `[${this.rangeSlider.value}]`;
    this.rangeSlider.oninput = () =>
      (this.inputDisplay.innerHTML = `[${this.rangeSlider.value}]`);
  };

  // The following method establishes a protocol that will be triggered...
  // if the user clicks the [submitButton] assigned to this class.
  buttonOnClickFunctionality() {
    this.submitButton.onclick = (evt) => {
      evt.preventDefault();
      console.log(`The active-user bets: ${this.rangeSlider.value}`);

      // If the user raises, then update the appropriate raise-counter.
      if (this.bettingRound === 'pre_flop') {
        preFlopRaiseCounter += 1;
        console.log(`Pre-flop Raise Count: ${preFlopRaiseCounter}`);
      } else if (this.bettingRound === 'post_flop') {
        postFlopRaiseCounter += 1;
        console.log(`Post-flop Raise Count: ${postFlopRaiseCounter}`);
      } else if (this.bettingRound === 'post_turn') {
        postTurnRaiseCounter += 1;
        console.log(`Post-turn Raise Count: ${postTurnRaiseCounter}`);
      } else if (this.bettingRound === 'post_river') {
        postRiverRaiseCounter += 1;
        console.log(`Post-river Raise Count: ${postRiverRaiseCounter}`);
      }

      // Hide the HTML elements aligned to: 1) this user-beting system...
      // 2) the 'fold' option, and 3) the 'check' / 'call' option.
      this.parentElement.hidden = true;
      foldButton.hidden = true;
      if (document.getElementById('check-btn')) {
        document.getElementById('check-btn').remove();
      }
      if (document.getElementById('call-btn')) {
        document.getElementById('call-btn').remove();
      }

      // Create a JSON-formatted object w/ key information...
      // (bet value + betting round) to send as an HTTP 'POST'...
      // request from the client to the server.
      let queryObject = {
        bet: this.rangeSlider.value,
        round: this.bettingRound,
      };

      // Execute the asynchronous [postBetVal()] function.
      postBetVal('/texas_hold_em/user_raise', queryObject);

      function postBetVal(path, queryObject) {
        try {
          axios.post(path, queryObject).then(
            (res) => {
              console.log(`Updated User Chips Commited: ${res.data}`);

              updateCommitedChips(userCommitedChips, res.data);
              updatePot();
              updateUserStack();
              // Execute the [cortanaResponse()] function, which triggers...
              // the ai-opp's decision making process in response to...
              // the active-user's bet.
              cortanaResponse();
            },
            (error) => {
              console.log(error);
            }
          );
        } catch (error) {
          console.log(error);
        }
      }

      async function cortanaResponse() {
        try {
          const res = await axios.get(
            `/texas_hold_em/ai_${queryObject['round']}_decision`
          );
          console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

          if (isNaN(res.data)) {
            window.location = '/texas_hold_em/ai_opp_fold';
          }

          console.log(`Updated AI Chips Commited: ${res.data}`);

          updateCommitedChips(oppCommitedChips, res.data);
          updatePot();
          updateOppStack();

          if (
            oppCommitedChips.children[1].innerText ==
            userCommitedChips.children[1].innerText
          ) {
            console.log('Cortana decided to call.');

            // If the ai-opp decides to call, display the appropriate...
            // button for users to advance to the next part of the hand.
            if (queryObject['round'] === 'pre_flop') {
              revealFlopButton.hidden = false;
            } else if (queryObject['round'] === 'post_flop') {
              revealTurnButton.hidden = false;
            } else if (queryObject['round'] === 'post_turn') {
              revealRiverButton.hidden = false;
            } else if (queryObject['round'] === 'post_river') {
              generateShowdownButton();
            }
          }

          if (
            oppCommitedChips.children[1].innerText !=
            userCommitedChips.children[1].innerText
          ) {
            console.log('Cortana decided to re-raise.');

            let raiseCount = 0;

            // Update the appropriate raise-counter.
            if (queryObject['round'] === 'pre_flop') {
              preFlopRaiseCounter += 1;
              raiseCount = preFlopRaiseCounter;
              console.log(`Pre-flop Raise Count: ${raiseCount}`);
            } else if (queryObject['round'] === 'post_flop') {
              postFlopRaiseCounter += 1;
              raiseCount = postFlopRaiseCounter;
              console.log(`Post-flop Raise Count: ${raiseCount}`);
            } else if (queryObject['round'] === 'post_turn') {
              postTurnRaiseCounter += 1;
              raiseCount = postTurnRaiseCounter;
              console.log(`Post-turn Raise Count: ${raiseCount}`);
            } else if (queryObject['round'] === 'post_river') {
              postRiverRaiseCounter += 1;
              raiseCount = postRiverRaiseCounter;
              console.log(`Post-river Raise Count: ${raiseCount}`);
            }

            // Generate a CALL button for users (+) reveal the FOLD button.
            generateCallButton(`user_${queryObject['round']}_call`);
            foldButton.hidden = false;

            // In each betting round of Texas Hold'em there can be one initial bet...
            // followed by a maximum of three raises. Users will have the option...
            // to re-raise "over-the-top" of their opponent, as long as this max...
            // limit has not been reached.
            if (raiseCount <= 3) {
              let reRaise = new Bet(
                queryObject['round'],
                allocatorContainer,
                allocator,
                allocatorValue,
                oppCommitedChips.children[1].innerText -
                  userCommitedChips.children[1].innerText +
                  1,
                userChipCount.children[1].innerText,
                allocatorSubmitButton
              );

              reRaise.revealUserBettingMechanism();
              reRaise.setMinBet();
              reRaise.setMaxBet();
              reRaise.setDefaultInputVal();
              reRaise.activateDisplay();
              reRaise.buttonOnClickFunctionality();
            } else {
              console.log(
                'The maximum number of raises in this round of betting has been reached.'
              );
            }
          }
        } catch (error) {
          console.log(error);
        }
      }
    };
  }
}

/* SECTION [3]: PRE-FLOP ACTION */

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
            'pre_flop',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          preFlopRaise.revealUserBettingMechanism();
          preFlopRaise.setMinBet();
          preFlopRaise.setMaxBet();
          preFlopRaise.setDefaultInputVal();
          preFlopRaise.activateDisplay();
          preFlopRaise.buttonOnClickFunctionality();
        } else if (
          oppCommitedChips.children[1].innerText > userBlind.innerText
        ) {
          console.log('Cortana decided to raise.');

          preFlopRaiseCounter += 1;
          console.log(`Pre-flop Raise Count: ${preFlopRaiseCounter}`);

          generateCallButton('/texas_hold_em/user_pre_flop_call');

          let preFlopRaise = new Bet(
            'pre_flop',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          preFlopRaise.revealUserBettingMechanism();
          preFlopRaise.setMinBet();
          preFlopRaise.setMaxBet();
          preFlopRaise.setDefaultInputVal();
          preFlopRaise.activateDisplay();
          preFlopRaise.buttonOnClickFunctionality();
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPreFlopDecision();
  } else {
    console.log('The action is on the active user.');
    generateCallButton('/texas_hold_em/user_pre_flop_call');

    let preFlopRaise = new Bet(
      'pre_flop',
      allocatorContainer,
      allocator,
      allocatorValue,
      oppCommitedChips.children[1].innerText -
        userCommitedChips.children[1].innerText +
        1,
      userChipCount.children[1].innerText,
      allocatorSubmitButton
    );

    preFlopRaise.revealUserBettingMechanism();
    preFlopRaise.setMinBet();
    preFlopRaise.setMaxBet();
    preFlopRaise.setDefaultInputVal();
    preFlopRaise.activateDisplay();
    preFlopRaise.buttonOnClickFunctionality();
  }
};

/* SECTION [4]: POST-FLOP ACTION */

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
  if (document.getElementById('username').innerText.includes('dealer')) {
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

        // Update the value associated w/ the number of...
        // chips the ai-opp has commited.
        updateCommitedChips(oppCommitedChips, res.data);

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

          let postFlopRaise = new Bet(
            'post_flop',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          postFlopRaise.revealUserBettingMechanism();
          postFlopRaise.setMinBet();
          postFlopRaise.setMaxBet();
          postFlopRaise.setDefaultInputVal();
          postFlopRaise.activateDisplay();
          postFlopRaise.buttonOnClickFunctionality();
        } else if (
          oppCommitedChips.children[1].innerText !=
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postFlopRaiseCounter += 1;
          console.log(`Post-flop Raise Count: ${postFlopRaiseCounter}`);
          generateCallButton('/texas_hold_em/user_post_flop_call');

          let postFlopRaise = new Bet(
            'post_flop',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          postFlopRaise.revealUserBettingMechanism();
          postFlopRaise.setMinBet();
          postFlopRaise.setMaxBet();
          postFlopRaise.setDefaultInputVal();
          postFlopRaise.activateDisplay();
          postFlopRaise.buttonOnClickFunctionality();
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPostFlopDecision();
  } else {
    console.log('The action is on the active user.');
    generateCheckButton('/texas_hold_em/user_post_flop_check');

    let postFlopRaise = new Bet(
      'post_flop',
      allocatorContainer,
      allocator,
      allocatorValue,
      oppCommitedChips.children[1].innerText -
        userCommitedChips.children[1].innerText +
        1,
      userChipCount.children[1].innerText,
      allocatorSubmitButton
    );

    postFlopRaise.revealUserBettingMechanism();
    postFlopRaise.setMinBet();
    postFlopRaise.setMaxBet();
    postFlopRaise.setDefaultInputVal();
    postFlopRaise.activateDisplay();
    postFlopRaise.buttonOnClickFunctionality();
  }
};

/* SECTION [5]: POST-TURN ACTION */

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

  if (document.getElementById('username').innerText.includes('dealer')) {
    console.log('The action is on Cortana.');

    async function cortanaPostTurnDecision() {
      try {
        const res = await axios.get('/texas_hold_em/ai_post_turn_decision');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        updateCommitedChips(oppCommitedChips, res.data);
        updatePot();
        updateOppStack();

        if (
          oppCommitedChips.children[1].innerText ==
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');

          generateCheckButton('/texas_hold_em/user_post_turn_check');

          let postTurnRaise = new Bet(
            'post_turn',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          postTurnRaise.revealUserBettingMechanism();
          postTurnRaise.setMinBet();
          postTurnRaise.setMaxBet();
          postTurnRaise.setDefaultInputVal();
          postTurnRaise.activateDisplay();
          postTurnRaise.buttonOnClickFunctionality();
        } else if (
          oppCommitedChips.children[1].innerText !=
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postTurnRaiseCounter += 1;
          console.log(`Post-turn Raise Count: ${postTurnRaiseCounter}`);
          generateCallButton('/texas_hold_em/user_post_turn_call');

          let postTurnRaise = new Bet(
            'post_turn',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          postTurnRaise.revealUserBettingMechanism();
          postTurnRaise.setMinBet();
          postTurnRaise.setMaxBet();
          postTurnRaise.setDefaultInputVal();
          postTurnRaise.activateDisplay();
          postTurnRaise.buttonOnClickFunctionality();
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPostTurnDecision();
  } else {
    console.log('The action is on the active user.');
    generateCheckButton('/texas_hold_em/user_post_turn_check');

    let postTurnRaise = new Bet(
      'post_turn',
      allocatorContainer,
      allocator,
      allocatorValue,
      oppCommitedChips.children[1].innerText -
        userCommitedChips.children[1].innerText +
        1,
      userChipCount.children[1].innerText,
      allocatorSubmitButton
    );

    postTurnRaise.revealUserBettingMechanism();
    postTurnRaise.setMinBet();
    postTurnRaise.setMaxBet();
    postTurnRaise.setDefaultInputVal();
    postTurnRaise.activateDisplay();
    postTurnRaise.buttonOnClickFunctionality();
  }
};

/* SECTION [6]: POST-RIVER ACTION */

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

  if (document.getElementById('username').innerText.includes('dealer')) {
    console.log('The action is on Cortana.');

    async function cortanaPostRiverDecision() {
      try {
        const res = await axios.get('/texas_hold_em/ai_post_river_decision');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        updateCommitedChips(oppCommitedChips, res.data);
        updatePot();
        updateOppStack();

        if (
          oppCommitedChips.children[1].innerText ==
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to check.');

          generateCheckButton('/texas_hold_em/user_post_river_check');

          let postRiverRaise = new Bet(
            'post_river',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          postRiverRaise.revealUserBettingMechanism();
          postRiverRaise.setMinBet();
          postRiverRaise.setMaxBet();
          postRiverRaise.setDefaultInputVal();
          postRiverRaise.activateDisplay();
          postRiverRaise.buttonOnClickFunctionality();
        } else if (
          oppCommitedChips.children[1].innerText !=
          userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to raise.');
          postRiverRaiseCounter += 1;
          console.log(`Post-river Raise Count: ${postRiverRaiseCounter}`);
          generateCallButton('/texas_hold_em/user_post_river_call');

          let postRiverRaise = new Bet(
            'post_river',
            allocatorContainer,
            allocator,
            allocatorValue,
            oppCommitedChips.children[1].innerText -
              userCommitedChips.children[1].innerText +
              1,
            userChipCount.children[1].innerText,
            allocatorSubmitButton
          );

          postRiverRaise.revealUserBettingMechanism();
          postRiverRaise.setMinBet();
          postRiverRaise.setMaxBet();
          postRiverRaise.setDefaultInputVal();
          postRiverRaise.activateDisplay();
          postRiverRaise.buttonOnClickFunctionality();
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPostRiverDecision();
  } else {
    console.log('The action is on the active user.');
    generateCheckButton('/texas_hold_em/user_post_river_check');

    let postRiverRaise = new Bet(
      'post_river',
      allocatorContainer,
      allocator,
      allocatorValue,
      oppCommitedChips.children[1].innerText -
        userCommitedChips.children[1].innerText +
        1,
      userChipCount.children[1].innerText,
      allocatorSubmitButton
    );

    postRiverRaise.revealUserBettingMechanism();
    postRiverRaise.setMinBet();
    postRiverRaise.setMaxBet();
    postRiverRaise.setDefaultInputVal();
    postRiverRaise.activateDisplay();
    postRiverRaise.buttonOnClickFunctionality();
  }
};
