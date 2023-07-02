document.addEventListener('DOMContentLoaded', function () {

    if (document.querySelector("#new-post-form")) {
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

        // Fix edit button
        var edit_btn = document.getElementsByClassName("edit-button");
        for (var i = 0; i < edit_btn.length; i++) {
            const item = edit_btn.item(i);
                item.onclick = () => {edit_post_pressed(item.dataset.postId); return false;};
        }
});


function edit_post_pressed(post_id) {
    content_item = document.getElementById(`post-content-${post_id}`)
    content = content_item.innerText
    content_item.innerHTML = "<textarea class=\"editarea\"></textarea><br/>"
    textarea_item = content_item.firstChild
    textarea_item.innerHTML = content
    edit_btn = document.getElementById(`edit-btn-${post_id}`)
    edit_btn.innerHTML = "Save"
    edit_btn.onclick = () => {
        content_item.innerHTML = '';
        var newText = document.createTextNode(textarea_item.value);
        content_item.appendChild(newText);
        edit_btn.innerHTML = "Edit"
        edit_btn.onclick = () => {edit_post_pressed(post_id); return false;};

        fetch(`/edit/${post_id}`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken() },
            credentials: 'same-origin', // Do not send CSRF token to another domain.
            body: JSON.stringify({
                post: textarea_item.value,
            })
    });
    return false;
    }
}

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
