// const BASE_URL = 'http://127.0.0.1:5000';

communityCards = document.getElementById('community-cards');

flopButton = document.getElementById('flop');

// let flop = sessionStorage.getItem('flop');

flopButton.onclick = async function revealFlop(evt) {
  evt.preventDefault();
  console.log('TEST');
  // console.log(flop);
  // for (card in flop) {
  //   communityCards.append(`<li>card</li>`);
  // }
};
