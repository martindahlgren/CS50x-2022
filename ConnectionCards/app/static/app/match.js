document.addEventListener('DOMContentLoaded', function () {
  console.log("Page has loaded!")

  // Try getting latest potential matches. I no one, display the time when the user should check back!
  change_text("Hello")


})

function change_text(text) {
  document.querySelector('#match-welcome-text').text = text;
}


function fill_matches(mailbox) {


}