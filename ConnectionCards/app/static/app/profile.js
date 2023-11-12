var no_more_matching = false

document.addEventListener('DOMContentLoaded', function () {
  console.log("Page has loaded!")

  document.querySelector('#edit-profile-form').addEventListener('submit', update_profile);

})

function update_profile(event) {
  event.preventDefault()
  const formFields = event.target.elements;
  fetch('/profileupdate', {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin', // Do not send CSRF token to another domain.  
    body: JSON.stringify({
      into_men: formFields.namedItem('into_men').checked,
      into_women: formFields.namedItem('into_women').checked,
      into_nb: formFields.namedItem('into_nb').checked,
      bio:  formFields.namedItem('bio').value,
    })
  })
    .then(response => {
      if (response.status == 200) {
        console.log("Updated profile")
      }
      else {
        document.querySelector('#message').innerText = "Error"
      }
    }).catch(() => { document.querySelector('#message').innerText = "Error" })
}
