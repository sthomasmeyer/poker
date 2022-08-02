const chipReloadButton = document.getElementById('chip-reload-btn');
const chipReloadAdvert = document.getElementById('chip-reload-advert');
const chipReloadMessage = document.getElementById('chip-reload-message');
const chipReloadSuccess = document.getElementById('chip-reload-success');
const navbar = document.getElementById('bootstrap-navbar');

navbar.setAttribute('hidden', true);

chipReloadButton.onclick = function (evt) {
  evt.preventDefault();
  chipReloadButton.remove();
  chipReloadMessage.remove();
  chipReloadAdvert.play();
  setTimeout(() => {
    let newMessage = document.createElement('h2');
    newMessage.innerText = "I'm never gonna let you down anon.";
    chipReloadSuccess.append(newMessage);

    let chipReloadConfirmation = document.createElement('p');
    chipReloadConfirmation.innerHTML = `25 chips have been added to your account`;
    chipReloadSuccess.append(chipReloadConfirmation);

    let homeButton = document.createElement('button');
    homeButton.innerText = 'Return to POK3R NIGHTS';
    homeButton.onclick = function (evt) {
      window.location = '/pok3r_nights';
    };
    chipReloadSuccess.append(homeButton);
  }, 3000);
};
