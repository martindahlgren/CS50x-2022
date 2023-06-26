document.addEventListener('DOMContentLoaded', function () {

    document.querySelector("#new-post-form").onsubmit = event => {

        event.preventDefault()
        const formFields = event.target.elements;

        fetch('/post', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken() },
            credentials: 'same-origin', // Do not send CSRF token to another domain.
            body: JSON.stringify({
                post: formFields.namedItem('new-post').value,
            })
        }).then(response => {
            if (response.status == 201) {
                response.json().then(json => {
                    // TODO: Consider something cooler here :)
                    window.location.replace(document.querySelector("#this-route").value);
                })
            }
        })

    }

    // Convert timezones to local
    var timestamps = document.getElementsByClassName("timestamp");
    for (var i = 0; i < timestamps.length; i++) {
        const item = timestamps.item(i);
        if (item.dataset.timezone == "utc")
        {
            let d = new Date(item.innerHTML);
            item.innerHTML = d.toLocaleString()
            item.dataset.timezone = "local"
        }
    }

    // Fix like button links
    var like_btns = document.getElementsByClassName("like-button");
    for (var i = 0; i < like_btns.length; i++) {
        const item = like_btns.item(i);
            item.onclick = () => {update_like_count(item.dataset.postId); return false;};
    }

});

function update_like_count(id) {
        
    fetch('/like', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken() },
        credentials: 'same-origin', // Do not send CSRF token to another domain.
        body: JSON.stringify({
            post_id: id,
        })
    }).then(response => {
        if (response.status == 201) {
            response.json().then(data => {
                like_count=data.like_count
                document.querySelector(`#like-count-${id}`).innerHTML = like_count;

            })
        }
    })


}

function csrftoken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}
