const playAgainButton = document.getElementById('congratulations-btn');
const navbar = document.getElementById('bootstrap-navbar');

navbar.setAttribute('hidden', true);

playAgainButton.onclick = function (evt) {
  window.location = '/pok3r_nights';
};
