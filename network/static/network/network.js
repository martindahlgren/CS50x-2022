document.addEventListener('DOMContentLoaded', function () {

    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    document.querySelector("#new-post-form").onsubmit = event => {

        event.preventDefault()
        const formFields = event.target.elements;

        fetch('/post', {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
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

});
