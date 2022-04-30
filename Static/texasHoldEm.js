// If the user is the dealer for a given hand, then an...
// HTML element w/ the following [id] will be auto-generated.
let preFlopCallButton = document.getElementById('pre-flop-call-btn');

// The following HTML elements are *always* generated...
// at the beginning of a hand, and they are revealed to...
// users when appropriate.
const revealFlopButton = document.getElementById('reveal-flop-btn');
const revealTurnButton = document.getElementById('reveal-turn-btn');
const revealRiverButton = document.getElementById('reveal-river-btn');

// The following variables capture elements related to...
// the "showdown" or the end of each poker hand. Note only...
// one set [win] / [loss] / [draw] will exist in a given hand.
const showdownDiv = document.getElementById('showdown');
const showdownWinForm = document.getElementById('showdown-win-form');
const showdownWinButton = document.getElementById('showdown-win-btn');
const showdownLossForm = document.getElementById('showdown-loss-form');
const showdownLossButton = document.getElementById('showdown-loss-btn');
const showdownDrawForm = document.getElementById('showdown-draw-form');
const showdownDrawButton = document.getElementById('showdown-draw-btn');

// The following variables capture elements related to...
// the active-user.
const userChipCount = document.getElementById('user-chip-count');
const userInitialStack = document.getElementById('user-initial-stack');
const userCommitedChips = document.getElementById('user-commited');
const userBlind = document.getElementById('user-blind');
const userScore = document.getElementById('user-score');
const userOptions = document.getElementById('user-options');

// The following [foldButton] variable is aligned to...
// the player's ever-present option to fold.
const foldButton = document.getElementById('fold-btn');

// The following variables capture elements related to...
// the community cards (+) the pot.
const communityCards = document.getElementById('community-cards');
const pot = document.getElementById('pot');
const sumOfBlinds = document.getElementById('sum-of-blinds');

// The following variables capture elements related to...
// the ai-opponent.
const oppHand = document.getElementById('ai-opp-hand');
const oppChipCount = document.getElementById('ai-opp-chip-count');
const oppInitialStack = document.getElementById('ai-opp-initial-stack');
const oppCommitedChips = document.getElementById('ai-opp-commited');
const oppBlind = document.getElementById('ai-opp-blind');
const oppScore = document.getElementById('ai-opp-score');

// The following "counter" variables are designed to track...
// the number of bets / raises in a given betting round.
let preFlopRaiseCounter = 0;
let postFlopRaiseCounter = 0;
let postTurnRaiseCounter = 0;
let postRiverRaiseCounter = 0;

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
        const res = await axios.get('/texas_hold_em/ai_pre_flop_action');
        console.log(`Cortana decided to fold: ${isNaN(res.data)}`);

        // If the GET request produces anything other than...
        // a number, specifically the number of chips...
        // that the ai-opp has decided to bet. Then they...
        // have chosen to fold this hand.
        if (isNaN(res.data)) {
          window.location = '/texas_hold_em/ai_opp_fold';
        }

        console.log(`AI Chips Commited: ${res.data}`);

        // Remove the DOM-element associated w/ the...
        // ai-opp's blind:
        oppBlind.remove();
        // Replace it with the updated number of chips...
        // they've chosen to commit:
        let updateCommited = document.createElement('td');
        updateCommited.innerText = `${res.data}`;
        oppCommitedChips.append(updateCommited);

        // Execute [updatePot()] + [updateOppStack()] functions.
        updatePot();
        updateOppStack();

        // The total number of chips in the pot is impacted...
        // by the ai-opp's decision, so it must be updated.
        async function updatePot() {
          try {
            const res = await axios.get('/texas_hold_em/update/pot');
            console.log(`Updated Pot Val: ${res.data}`);

            // Remove the DOM-element associated w/ the...
            // initial value of the pot:
            sumOfBlinds.remove();
            // Replace it with the updated value:
            let updatePot = document.createElement('td');
            updatePot.innerText = res.data;
            pot.append(updatePot);
          } catch (error) {
            console.log(error);
          }
        }

        // The number of chips in the ai-opp's stack is...
        // impacted by their decision, so it must be updated.
        async function updateOppStack() {
          try {
            const res = await axios.get(
              '/texas_hold_em/update/ai_opp_chip_count'
            );
            console.log(`Updated Opp Stack: ${res.data}`);
            // Remove the DOM-element associated w/ the...
            // initial value of the ai-opp's stack:
            oppInitialStack.remove();
            // Replace it with the updated value:
            let updateOppStack = document.createElement('td');
            updateOppStack.innerText = res.data;
            oppChipCount.append(updateOppStack);
          } catch (error) {
            console.log(error);
          }
        }

        if (updateCommited.innerText == userBlind.innerText) {
          console.log('Cortana decided to call.');
          // If Cortana calls, then the active-user can check.
          let preFlopCheckButton = document.createElement('button');
          preFlopCheckButton.innerText = 'Check';
          userOptions.append(preFlopCheckButton);

          // This [if]-statement is designed to check whether...
          // or not the active-user has the option to check.
          if (preFlopCheckButton != null) {
            preFlopCheckButton.onclick = function userAction(evt) {
              evt.preventDefault();
              // If the user chooses to check, then take away the...
              // option to fold, and display the [revealFlopButton].
              foldButton.hidden = true;
              // Don't forget to delete this [preFlopCheckbutton].
              preFlopCheckButton.remove();
              revealFlopButton.hidden = false;
            };
          }
        }

        if (updateCommited.innerText > userBlind.innerText) {
          console.log('Cortana decided to raise.');

          preFlopRaiseCounter += 1;
          console.log(`Pre-flop Raise Count: ${preFlopRaiseCounter}`);

          // If Cortana raises, then the active-user can call.
          let preFlopCallButton = document.createElement('button');
          preFlopCallButton.setAttribute('id', 'pre-flop-call-btn');
          preFlopCallButton.innerText = 'Call';
          userOptions.append(preFlopCallButton);

          // This [if]-statement is designed to check whether...
          // or not the active-user has the option to call.
          if (preFlopCallButton != null) {
            preFlopCallButton.onclick = function userAction(evt) {
              evt.preventDefault();

              // Execute the asynchronous [preFlopCall()] function.
              preFlopCall();

              // If the user chooses to call, then take away the...
              // option to fold, and display the [revealFlopButton].
              foldButton.hidden = true;
              // Don't forget to delete this [preFlopCallbutton].
              preFlopCallButton.remove();
              revealFlopButton.hidden = false;

              async function preFlopCall() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_pre_flop_call'
                  );
                  console.log(`User Chips Commited: ${res.data}`);
                  userBlind.remove();
                  let updateCommited = document.createElement('td');
                  updateCommited.innerText = `${res.data}`;
                  userCommitedChips.append(updateCommited);
                  updatePot();
                  updateUserStack();

                  // The total number of chips in the pot is impacted...
                  // by the active-user's decision, so it must be updated.
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

                  // The number of chips in the active-user's stack is...
                  // impacted by their decision, so it must be updated.
                  async function updateUserStack() {
                    try {
                      const res = await axios.get(
                        '/texas_hold_em/update/user_chip_count'
                      );
                      console.log(`Updated User Stack: ${res.data}`);
                      // Remove the DOM-element associated w/ the...
                      // initial value of the ai-opp's stack:
                      userInitialStack.remove();
                      // Replace it with the updated value.
                      let updateUserStack = document.createElement('td');
                      updateUserStack.innerText = res.data;
                      userChipCount.append(updateUserStack);
                    } catch (error) {
                      console.log(error);
                    }
                  }
                } catch (error) {
                  console.log(error);
                }
              }
            };
          }
        }
      } catch (error) {
        console.log(error);
      }
    }
    cortanaPreFlopDecision();
  } else {
    console.log('The action is on the active user.');
  }
};

// This [if]-statement is designed to check whether...
// or not the active-user has the option to call.
if (preFlopCallButton != null) {
  preFlopCallButton.onclick = function userAction(evt) {
    evt.preventDefault();

    // Execute the asynchronous [preFlopCall()] function.
    preFlopCall();

    // If the user chooses to call, then take away the...
    // option to fold, and display the [revealFlopButton].
    foldButton.hidden = true;
    // Don't forget to delete this [preFlopCallbutton].
    preFlopCallButton.remove();
    revealFlopButton.hidden = false;

    async function preFlopCall() {
      try {
        const res = await axios.get('/texas_hold_em/user_pre_flop_call');
        console.log(`User Chips Commited: ${res.data}`);
        userBlind.remove();
        let updateCommited = document.createElement('td');
        updateCommited.innerText = `${res.data}`;
        userCommitedChips.append(updateCommited);
        updatePot();
        updateUserStack();

        async function updatePot() {
          try {
            const res = await axios.get('/texas_hold_em/update/pot');
            console.log(`Updated Pot Val: ${res.data}`);
            sumOfBlinds.remove();
            let updatePot = document.createElement('td');
            updatePot.innerText = res.data;
            pot.append(updatePot);
          } catch (error) {
            console.log(error);
          }
        }

        async function updateUserStack() {
          try {
            const res = await axios.get(
              '/texas_hold_em/update/user_chip_count'
            );
            console.log(`Updated User Stack: ${res.data}`);
            userInitialStack.remove();
            let updateUserStack = document.createElement('td');
            updateUserStack.innerText = res.data;
            userChipCount.append(updateUserStack);
          } catch (error) {
            console.log(error);
          }
        }
      } catch (error) {
        console.log(error);
      }
    }
  };
}

revealFlopButton.onclick = function revealFlop(evt) {
  evt.preventDefault();

  getFlop();
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

  revealFlopButton.remove();
  newBtn = document.createElement('button');
  newBtn.setAttribute('id', 'call-post-flop-btn');
  newBtn.innerText = 'Call';
  document.getElementById('user-options').append(newBtn);
  let callPostFlopButton = document.getElementById('call-post-flop-btn');
  foldButton.hidden = false;

  callPostFlopButton.onclick = function keepPlaying(evt) {
    evt.preventDefault();
    callPostFlopButton.remove();
    foldButton.hidden = true;
    revealTurnButton.hidden = false;
  };
};

revealTurnButton.onclick = function revealTurn(evt) {
  evt.preventDefault();

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

  revealTurnButton.remove();
  newBtn = document.createElement('button');
  newBtn.setAttribute('id', 'call-post-turn-btn');
  newBtn.innerText = 'Call';
  document.getElementById('user-options').append(newBtn);
  let callPostTurnButton = document.getElementById('call-post-turn-btn');
  foldButton.hidden = false;

  callPostTurnButton.onclick = function keepPlaying(evt) {
    evt.preventDefault();
    callPostTurnButton.remove();
    foldButton.hidden = true;
    revealRiverButton.hidden = false;
  };
};

revealRiverButton.onclick = function revealRiver(evt) {
  evt.preventDefault();

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

  revealRiverButton.remove();
  newBtn = document.createElement('button');
  newBtn.setAttribute('id', 'call-post-river-btn');
  newBtn.innerText = 'Call';
  document.getElementById('user-options').append(newBtn);
  let callPostRiverButton = document.getElementById('call-post-river-btn');
  foldButton.hidden = false;

  callPostRiverButton.onclick = function finishTheHand(evt) {
    evt.preventDefault();
    callPostRiverButton.remove();
    foldButton.hidden = true;
    showdownDiv.hidden = false;
  };
};

// This final section of code deals w/ the showdown.

// This [if]-statement is designed to check whether...
// or not the active-user has WON the hand, and...
// if they have, then the appropriate steps are taken.
if (showdownWinButton != null) {
  showdownWinButton.onclick = function showdown(evt) {
    evt.preventDefault();
    setTimeout(() => {
      showdownWinForm.submit();
    }, 1000);
    showdownWinButton.remove();

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
    getOppCards();

    async function getUserScore() {
      try {
        const res = await axios.get('/texas_hold_em/user_score');
        console.log(`User Score: ${res.data}`);
        displayScore = document.createElement('td');
        displayScore.innerText = `${res.data}`;
        userScore.append(displayScore);
      } catch (error) {
        console.log(error);
      }
    }
    getUserScore();

    async function getOppScore() {
      try {
        const res = await axios.get('/texas_hold_em/computer_opp_score');
        console.log(`Opp Score: ${res.data}`);
        displayScore = document.createElement('td');
        if (res.data > 1) {
          displayScore.innerText = res.data;
          oppScore.append(displayScore);
        }
      } catch (error) {
        console.log(error);
      }
    }
    getOppScore();

    setTimeout(() => {
      alert(`
      You've won this hand
      Press 'OK' to see the next hand
      `);
    }, 500);
  };
}

// This [if]-statement is designed to check whether...
// or not the active-user has LOST the hand, and...
// if they have, then the appropriate steps are taken.
if (showdownLossButton != null) {
  showdownLossButton.onclick = function showdown(evt) {
    evt.preventDefault();
    setTimeout(() => {
      showdownLossForm.submit();
    }, 1000);
    showdownLossButton.remove();

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
    getOppCards();

    async function getUserScore() {
      try {
        const res = await axios.get('/texas_hold_em/user_score');
        console.log(`User Score: ${res.data}`);
        displayScore = document.createElement('td');
        displayScore.innerText = `${res.data}`;
        userScore.append(displayScore);
      } catch (error) {
        console.log(error);
      }
    }
    getUserScore();

    async function getOppScore() {
      try {
        const res = await axios.get('/texas_hold_em/computer_opp_score');
        console.log(`Opp Score: ${res.data}`);
        displayScore = document.createElement('td');
        if (res.data > 1) {
          displayScore.innerText = res.data;
          oppScore.append(displayScore);
        }
      } catch (error) {
        console.log(error);
      }
    }
    getOppScore();

    setTimeout(() => {
      alert(`
      You've lost this hand
      Press 'OK' to see the next hand
      `);
    }, 500);
  };
}

// This [if]-statement is designed to check whether...
// or not the hand ended in a DRAW.
if (showdownDrawButton != null) {
  showdownDrawButton.onclick = function showdown(evt) {
    evt.preventDefault();
    setTimeout(() => {
      showdownDrawForm.submit();
    }, 1000);
    showdownDrawButton.remove();

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
    getOppCards();

    async function getUserScore() {
      try {
        const res = await axios.get('/texas_hold_em/user_score');
        console.log(`User Score: ${res.data}`);
        displayScore = document.createElement('td');
        displayScore.innerText = `${res.data}`;
        userScore.append(displayScore);
      } catch (error) {
        console.log(error);
      }
    }
    getUserScore();

    async function getOppScore() {
      try {
        const res = await axios.get('/texas_hold_em/computer_opp_score');
        console.log(`Opp Score: ${res.data}`);
        displayScore = document.createElement('td');
        if (res.data > 1) {
          displayScore.innerText = res.data;
          oppScore.append(displayScore);
        }
      } catch (error) {
        console.log(error);
      }
    }
    getOppScore();

    setTimeout(() => {
      alert(`
      This hand ended in a draw
      Press 'OK' to see the next hand
      `);
    }, 500);
  };
}
