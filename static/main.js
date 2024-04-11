console.log("Sanity check!");

fetch("https://raspberryeclair.azurewebsites.net/config")
.then((result) => { return result.json(); })
.then((data) => {
  const stripe = Stripe(data.publicKey);
  document.querySelector("#bookingForm").addEventListener("submit", () => {
    fetch("https://raspberryeclair.azurewebsites.net/create-checkout-session")
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });
});