console.log("Sanity check!");

fetch("/config")
.then((result) => { return result.json(); })
.then((data) => {
  const stripe = Stripe(data.publicKey);
  document.querySelector("#bookingForm").addEventListener("submit", () => {
    fetch("/create-checkout-session") 
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