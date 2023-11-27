var no_more_matching = false

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
  seconds = data.seconds_to_next
  if (seconds <= 60)
  {
    change_text(`No new profiles available, check again in ${seconds} seconds`)
  }
  else if (seconds <= 3600)
  {
    change_text(`No new profiles available, check again in ${Math.round(seconds/60)} minutes`)
  }
  else
  {
    change_text(`No new profiles available, check again in ${Math.round(seconds/3600)} hours`)
  }
}

function on_click_card(card_html)
{
  if (card_html.classList.contains("clicked-card"))
  {
    return;
  }
  if (no_more_matching)
  {
    return;
  }

  card_html.classList.add("clicked-card")
  fetch('/send_swipe', {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin', // Do not send CSRF token to another domain.
    body: JSON.stringify({
      "id": card_html.dataset.id,
    })
  }).then(response => {
    if (response.ok) {
      return response.json();
    }
  }).then(data => {
    if(data.match_already)
    {
      change_text("You got a match! Let's go make some conversation.");
    }
    else if(data.n_swipes_left != 0 )
    {
      change_text("Check Messages later to find out if you got a match");
    }
    else
    {
      change_text("You have no clicks left. Come by Messages later!");
    }
    if (data.n_swipes_left == 0)
    {
      no_more_matching = true
    }
  });


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
    let card_html = cards_html[index]
    card_html.classList.remove('empty-card');
    card_html.dataset = card_html.dataset || {}
    card_html.dataset.id = swipee.id;
    card_html.innerHTML = 
      `<img src="${swipee.picture}">
      <h2 class=profile-name>${swipee.name}</h2>
      <p id=profiletext_${index}></p>`;
      card_html.onclick = (() => on_click_card(card_html));
      document.querySelector(`#profiletext_${index}`).innerText = swipee.bio;
      
    }

  for (const card_html of document.querySelectorAll('.empty-card')) {
    card_html.innerText = "No profile available";
    delete card_html.onclick
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
