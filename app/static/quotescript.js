const quoteBtn = document.querySelector("#getQuote");
const quote = document.querySelector("#quoteSlip");
const apiUrl = 'https://cloud.iexapis.com/stable/stock/';
const qtk = '/quote?token=pk_95d7f54ba98547d3a67b8b8a88c7bf70';

function getQuote() {
  var input = document.querySelector(".UserInput").value;
  var url= (apiUrl + input + qtk);
  fetch(url).then(function(response) {
    // Shorthand to check for an HTTP 2xx response status.
    // See https://fetch.spec.whatwg.org/#dom-response-ok
    if (response.ok) {
      return response;
    }
    // Raise an exception to reject the promise and trigger the outer .catch() handler.
    // By default, an error response status (4xx, 5xx) does NOT cause the promise to reject!
    throw Error(response.statusText);
  }).then(function(response) {
    return response.json();
  }).then(function(json) {
    quotation = `${json.symbol} (${json.companyName}) worths $${json.latestPrice} per share.`;
    console.log(json)
    quote.innerText = quotation;
  }).catch(function(error) {
    console.log('Request failed:', error.message);
    quotation = `No Data associated with ${input.toUpperCase()}`;
    quote.innerText = quotation;
  });
}

quoteBtn.addEventListener('click', getQuote);