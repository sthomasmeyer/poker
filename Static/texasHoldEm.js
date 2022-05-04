/* SECTION [0]: ESTABLISHING KEY VARIABLES */

// If the user is the dealer for a given hand, then an...
// HTML element w/ the following [id] will be auto-generated.
let preFlopCallButton = document.getElementById('pre-flop-call-btn');

// If the ai-opp is the delaer, then the active-user will...
// be the first to act in each post-flop round of betting...
// and they will always have the option to check. Note...
// if the active-user is the dealer, then these buttons...
// will *not* be auto-generated.
let postFlopCheckButton = document.getElementById('post-flop-check-btn');
let postTurnCheckButton = document.getElementById('post-turn-check-btn');
let postRiverCheckButton = document.getElementById('post-river-check-btn');

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

/* SECTION [1]: PRE-FLOP ACTION */

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

          // Even though users are technically allowed to fold...
          // it would be foolish to do so.
          foldButton.hidden = true;

          // This [if]-statement is designed to check whether...
          // or not the active-user has the option to check.
          if (preFlopCheckButton != null) {
            preFlopCheckButton.onclick = function userAction(evt) {
              evt.preventDefault();

              // Don't forget to delete this [preFlopCheckButton].
              preFlopCheckButton.remove();
              // If the user decides to check, then...
              // display the [revealFlop] button.
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

/* SECTION [2]: POST-FLOP ACTION */

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

        // Remove the (outdated) DOM-element associated...
        // w/ the ai-opp's number of commited chips:
        oppCommitedChips.children[1].remove();
        // Replace it with the updated number of chips...
        // they've chosen to commit:
        let updateCommited = document.createElement('td');
        updateCommited.innerText = totalCommitedChips;
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

            // Remove the (outdated) DOM-element associated...
            // w/ the value of the pot:
            pot.removeChild(pot.children[1]);
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
            // Remove the (outdated) DOM-element associated
            // w/ the value of the ai-opp's stack:
            oppChipCount.children[1].remove();
            // Replace it with the updated value:
            let updateOppStack = document.createElement('td');
            updateOppStack.innerText = res.data;
            oppChipCount.append(updateOppStack);
          } catch (error) {
            console.log(error);
          }
        }

        // This [if]-statement is designed to check whether...
        // or not the ai-opp has checked.
        if (
          updateCommited.innerText == userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');
          // If Cortana checks, then the active-user can check.
          let postFlopCheckButton = document.createElement('button');
          postFlopCheckButton.innerText = 'Check';
          userOptions.append(postFlopCheckButton);

          // This [if]-statement is designed to check whether...
          // or not the active-user has the option to check...
          // Remember, if you attempt to add an [onclick] event...
          // to a non-existent button, then errors will be thrown.
          if (postFlopCheckButton != null) {
            postFlopCheckButton.onclick = function userAction(evt) {
              evt.preventDefault();

              // Execute the asynchronous [postFlopCheck()] function.
              postFlopCheck();

              // Don't forget to delete this [postFlopCheckbutton].
              postFlopCheckButton.remove();
              // If the user decides to check, then...
              // display the [revealTurn] button.
              revealTurnButton.hidden = false;

              async function postFlopCheck() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_post_flop_check'
                  );
                  console.log(
                    `[CHECK] Post-flop User Chips Commited: ${res.data}`
                  );
                } catch (error) {
                  console.log(error);
                }
              }
            };
          }
        }

        if (
          updateCommited.innerText > userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postFlopRaiseCounter += 1;
          console.log(`Post-flop Raise Count: ${postFlopRaiseCounter}`);

          // If the ai-opp raises, then users can fold.
          foldButton.hidden = false;

          // If Cortana raises, then the active-user can call.
          let postFlopCallButton = document.createElement('button');
          postFlopCallButton.innerText = 'Call';
          userOptions.append(postFlopCallButton);

          // This [if]-statement is designed to check whether...
          // or not the active-user has the option to call.
          if (postFlopCallButton != null) {
            postFlopCallButton.onclick = function userAction(evt) {
              evt.preventDefault();

              // Execute the asynchronous [preFlopCall()] function.
              postFlopCall();

              // If the user chooses to call, then take away the...
              // option to fold, and display the [revealFlopButton].
              foldButton.hidden = true;
              // Don't forget to delete this [preFlopCallbutton].
              postFlopCallButton.remove();
              // If the user decides to call, then...
              // display the [revealTurn] button.
              revealTurnButton.hidden = false;

              async function postFlopCall() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_post_flop_call'
                  );

                  totalCommitedChips =
                    Number(userCommitedChips.children[1].innerText) + res.data;

                  console.log(`Post-flop User Chips Commited: 
                  ${userCommitedChips.children[1].innerText} + ${res.data} = ${totalCommitedChips}`);

                  // Remove the (outdated) DOM-element associated...
                  // w/ the ai-opp's number of commited chips:
                  userCommitedChips.children[1].remove();
                  // Replace it with the updated number of chips...
                  // they've chosen to commit:
                  let updateCommited = document.createElement('td');
                  updateCommited.innerText = totalCommitedChips;
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
                      userChipCount.children[1].remove();
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
    cortanaPostFlopDecision();
  } else {
    console.log('The action is on the active user.');
    postFlopCheckButton.hidden = false;
  }
};

// This [if]-statement is designed to check whether...
// or not the active-user has the option to check.
if (postFlopCheckButton != null) {
  postFlopCheckButton.onclick = function userAction(evt) {
    evt.preventDefault();

    // Execute the asynchronous [postFlopCheck()] function.
    postFlopCheck();

    // If the user chooses to check, then take away the...
    // option to fold, and display the [revealTurnButton].
    foldButton.hidden = true;
    // Don't forget to delete this [postFlopCheckButton].
    postFlopCheckButton.remove();
    revealTurnButton.hidden = false;

    async function postFlopCheck() {
      try {
        const res = await axios.get('/texas_hold_em/user_post_flop_check');
        console.log(`[CHECK] Post-flop User Chips Commited: ${res.data}`);
      } catch (error) {
        console.log(error);
      }
    }
  };
}

/* SECTION [3]: POST-TURN ACTION */

revealTurnButton.onclick = function revealTurn(evt) {
  evt.preventDefault();

  getTurn();

  revealTurnButton.remove();

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

        oppCommitedChips.children[1].remove();

        let updateCommited = document.createElement('td');
        updateCommited.innerText = totalCommitedChips;
        oppCommitedChips.append(updateCommited);

        updatePot();
        updateOppStack();

        async function updatePot() {
          try {
            const res = await axios.get('/texas_hold_em/update/pot');
            console.log(`Updated Pot Val: ${res.data}`);

            pot.removeChild(pot.children[1]);

            let updatePot = document.createElement('td');
            updatePot.innerText = res.data;
            pot.append(updatePot);
          } catch (error) {
            console.log(error);
          }
        }

        async function updateOppStack() {
          try {
            const res = await axios.get(
              '/texas_hold_em/update/ai_opp_chip_count'
            );
            console.log(`Updated Opp Stack: ${res.data}`);

            oppChipCount.children[1].remove();

            let updateOppStack = document.createElement('td');
            updateOppStack.innerText = res.data;
            oppChipCount.append(updateOppStack);
          } catch (error) {
            console.log(error);
          }
        }

        if (
          updateCommited.innerText == userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');

          let postTurnCheckButton = document.createElement('button');
          postTurnCheckButton.innerText = 'Check';
          userOptions.append(postTurnCheckButton);

          if (postTurnCheckButton != null) {
            postTurnCheckButton.onclick = function userAction(evt) {
              evt.preventDefault();

              postTurnCheck();

              postTurnCheckButton.remove();

              revealRiverButton.hidden = false;

              async function postTurnCheck() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_post_turn_check'
                  );
                  console.log(
                    `[CHECK] Post-turn User Chips Commited: ${res.data}`
                  );
                } catch (error) {
                  console.log(error);
                }
              }
            };
          }
        }

        if (
          updateCommited.innerText > userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postTurnRaiseCounter += 1;
          console.log(`Post-turn Raise Count: ${postTurnRaiseCounter}`);

          foldButton.hidden = false;

          let postTurnCallButton = document.createElement('button');
          postTurnCallButton.innerText = 'Call';
          userOptions.append(postTurnCallButton);

          if (postTurnCallButton != null) {
            postTurnCallButton.onclick = function userAction(evt) {
              evt.preventDefault();

              postTurnCall();

              foldButton.hidden = true;

              postTurnCallButton.remove();

              revealRiverButton.hidden = false;

              async function postTurnCall() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_post_turn_call'
                  );

                  totalCommitedChips =
                    Number(userCommitedChips.children[1].innerText) + res.data;

                  console.log(`Post-turn User Chips Commited: 
                  ${userCommitedChips.children[1].innerText} + ${res.data} = ${totalCommitedChips}`);

                  userCommitedChips.children[1].remove();

                  let updateCommited = document.createElement('td');
                  updateCommited.innerText = totalCommitedChips;
                  userCommitedChips.append(updateCommited);

                  updatePot();
                  updateUserStack();

                  async function updatePot() {
                    try {
                      const res = await axios.get('/texas_hold_em/update/pot');
                      console.log(`Updated Pot Val: ${res.data}`);

                      pot.removeChild(pot.children[1]);

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

                      userChipCount.children[1].remove();

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
    cortanaPostTurnDecision();
  } else {
    console.log('The action is on the active user.');
    postTurnCheckButton.hidden = false;
  }
};

if (postTurnCheckButton != null) {
  postTurnCheckButton.onclick = function userAction(evt) {
    evt.preventDefault();

    postTurnCheck();

    foldButton.hidden = true;
    postTurnCheckButton.remove();
    revealRiverButton.hidden = false;

    async function postTurnCheck() {
      try {
        const res = await axios.get('/texas_hold_em/user_post_turn_check');
        console.log(`[CHECK] Post-turn User Chips Commited: ${res.data}`);
      } catch (error) {
        console.log(error);
      }
    }
  };
}

/* SECTION [4]: POST-RIVER ACTION */

revealRiverButton.onclick = function revealRiver(evt) {
  evt.preventDefault();

  getRiver();

  revealRiverButton.remove();

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

        oppCommitedChips.children[1].remove();

        let updateCommited = document.createElement('td');
        updateCommited.innerText = totalCommitedChips;
        oppCommitedChips.append(updateCommited);

        updatePot();
        updateOppStack();

        async function updatePot() {
          try {
            const res = await axios.get('/texas_hold_em/update/pot');
            console.log(`Updated Pot Val: ${res.data}`);

            pot.removeChild(pot.children[1]);

            let updatePot = document.createElement('td');
            updatePot.innerText = res.data;
            pot.append(updatePot);
          } catch (error) {
            console.log(error);
          }
        }

        async function updateOppStack() {
          try {
            const res = await axios.get(
              '/texas_hold_em/update/ai_opp_chip_count'
            );
            console.log(`Updated Opp Stack: ${res.data}`);

            oppChipCount.children[1].remove();

            let updateOppStack = document.createElement('td');
            updateOppStack.innerText = res.data;
            oppChipCount.append(updateOppStack);
          } catch (error) {
            console.log(error);
          }
        }

        if (
          updateCommited.innerText == userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana has decided to check.');

          let postRiverCheckButton = document.createElement('button');
          postRiverCheckButton.innerText = 'Check';
          userOptions.append(postRiverCheckButton);

          if (postRiverCheckButton != null) {
            postRiverCheckButton.onclick = function userAction(evt) {
              evt.preventDefault();

              postRiverCheck();

              postRiverCheckButton.remove();

              showdownDiv.hidden = false;

              async function postRiverCheck() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_post_river_check'
                  );
                  console.log(
                    `[CHECK] Post-river User Chips Commited: ${res.data}`
                  );
                } catch (error) {
                  console.log(error);
                }
              }
            };
          }
        }

        if (
          updateCommited.innerText > userCommitedChips.children[1].innerText
        ) {
          console.log('Cortana decided to raise.');
          postRiverRaiseCounter += 1;
          console.log(`Post-river Raise Count: ${postRiverRaiseCounter}`);

          foldButton.hidden = false;

          let postRiverCallButton = document.createElement('button');
          postRiverCallButton.innerText = 'Call';
          userOptions.append(postRiverCallButton);

          if (postRiverCallButton != null) {
            postRiverCallButton.onclick = function userAction(evt) {
              evt.preventDefault();

              postRiverCall();

              foldButton.hidden = true;

              postRiverCallButton.remove();

              showdownDiv.hidden = false;

              async function postRiverCall() {
                try {
                  const res = await axios.get(
                    '/texas_hold_em/user_post_river_call'
                  );

                  totalCommitedChips =
                    Number(userCommitedChips.children[1].innerText) + res.data;

                  console.log(`Post-river User Chips Commited: 
                  ${userCommitedChips.children[1].innerText} + ${res.data} = ${totalCommitedChips}`);

                  userCommitedChips.children[1].remove();

                  let updateCommited = document.createElement('td');
                  updateCommited.innerText = totalCommitedChips;
                  userCommitedChips.append(updateCommited);

                  updatePot();
                  updateUserStack();

                  async function updatePot() {
                    try {
                      const res = await axios.get('/texas_hold_em/update/pot');
                      console.log(`Updated Pot Val: ${res.data}`);

                      pot.removeChild(pot.children[1]);

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

                      userChipCount.children[1].remove();

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
    cortanaPostRiverDecision();
  } else {
    console.log('The action is on the active user.');
    postRiverCheckButton.hidden = false;
  }
};

if (postRiverCheckButton != null) {
  postRiverCheckButton.onclick = function userAction(evt) {
    evt.preventDefault();

    postRiverCheck();

    foldButton.hidden = true;
    postRiverCheckButton.remove();
    showdownDiv.hidden = false;

    async function postRiverCheck() {
      try {
        const res = await axios.get('/texas_hold_em/user_post_river_check');
        console.log(`[CHECK] Post-river User Chips Commited: ${res.data}`);
      } catch (error) {
        console.log(error);
      }
    }
  };
}

/* SECTION [5]: SHOWDOWN */

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
