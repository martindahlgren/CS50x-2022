document.addEventListener('DOMContentLoaded', function () {
  console.log("Page has loaded!")

  // Try getting latest potential matches. I no one, display the time when the user should check back!
  update_matches()

})

function change_text(text) {
  document.querySelector('#match-welcome-text').innerText = text;
}

function no_profiles(data)
{
  hours = data.hours_to_next
  if (Math.round(hours) <= 1)
  {
    change_text(`No new profiles available, check again in ${Math.round(hours*60)} minutes`)
  }
  else
  {
    change_text(`No new profiles available, check again in ${Math.round(hours)} hours`)
  }
}

function on_click_card(card_html)
{
  fetch('/send_swipe', {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin', // Do not send CSRF token to another domain.
    body: JSON.stringify({
      "id": card_html.dataset.id,
    })
    
})
// TODO: Do something cool here :)
/*.then(response => {

})
*/
}


function fill_matches(data)
{
  cards_html = [
    document.querySelector('#card1'),
    document.querySelector('#card2'),
    document.querySelector('#card3'),
    document.querySelector('#card4')]
  swipees = data.swipees
  for (const [index, swipee] of swipees.entries()) {
    console.log(swipee)
    card_html = cards_html[index]
    card_html.classList.remove('empty-card');
    card_html.dataset = card_html.dataset || {}
    card_html.dataset.id = swipee.id;
    card_html.innerHTML = 
      `<img src="${swipee.picture}">
      <h2>${swipee.name}</h2>
      <p>${swipee.bio}</p>`;
      card_html.onclick = (() => on_click_card(card_html));
    }

  for (const card of document.querySelectorAll('.empty-card')) {
    card.innerText = "No profile available";
  }

}


function update_matches() {

  fetch('/get_candidates')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if(data.n_swipes_left == 0)
      {
        no_profiles(data)
      }
      else
      {
        fill_matches(data)
        if(data.n_swipes_left == 1)
        {
          change_text(`Select a Lovely Profile`)
        }
        else
        {
          change_text(`Select Two Lovely Profiles`)
        }
      }
    }).catch(error => {
      console.error('Error fetching data:', error);
      change_text("An error occurred :(")
    });;

}
