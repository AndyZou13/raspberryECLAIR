console.log("Sanity check!");

fetch("http://127.0.0.1:5000/config")
.then((result) => { return result.json(); })
.then((data) => {
  const stripe = Stripe(data.publicKey);
  document.querySelector("#bookingForm").addEventListener("submit", () => {
    console.log("Sanity check!");
    fetch("http://127.0.0.1:5000/create-checkout-session")
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