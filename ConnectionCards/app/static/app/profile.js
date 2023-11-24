var no_more_matching = false
var city_filter;

document.addEventListener('DOMContentLoaded', function () {
  console.log("Page has loaded!")

  document.querySelector('#edit-profile-form').addEventListener('submit', update_profile);
  city_filter = document.querySelector('#city-filter')

  city_filter.addEventListener('keyup', filter_cities);


})


function filter_cities(event) {
  filter = city_filter.value

  fetch('/suggest_cities', {
    method: 'POST', // TODO: Switch to using GET
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin', // Do not send CSRF token to another domain.  
    body: JSON.stringify({
      filter: filter,
    })
  })
    .then(response => {
      if (response.status == 200) {
        response.json().then(data => {add_city_options(data["possible_cities"])})
      }
      else {
        add_city_options([]);
        document.querySelector('#message').innerText = "Error"
      }
    }).catch(() => { add_city_options([]); document.querySelector('#message').innerText = "Error" })
}

function add_city_options(cities)
{
  radios = document.querySelector('#cities-radios')
  innerHTML = ""
  for (const city of cities) {
    innerHTML += `
      <div>
      <input type="radio" name="city" value="${city["city_id"]}" id="city_${city["city_id"]}" />
      <label for="city_${city["city_id"]}">${city["display_name"]}</label>
      </div>
    `
  }

  if (cities.length == 0) {
    innerHTML = `
    <div>
    <input type="radio" name="city" value="" id="city_invalid" />
    <label for="city_invalid">No matching cities</label>
    </div>
  `
  }
  radios.innerHTML = innerHTML
}


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
      location:  formFields.namedItem('city').value,
    })
  })
    .then(response => {
      if (response.status == 200) {
        document.querySelector('#message').innerText = "Updated profile"
      }
      else {
        document.querySelector('#message').innerText = "Error"
      }
    }).catch(() => { document.querySelector('#message').innerText = "Error" })
}
