document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // Send email event listener
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function send_email(event) {
  event.preventDefault()
  const formFields = event.target.elements;
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: formFields.namedItem('compose-recipients').value,
      subject: formFields.namedItem('compose-subject').value,
      body: formFields.namedItem('compose-body').value
    })
  })
    .then(response => {
      if (response.status == 201) {
        load_mailbox('sent')
      }
      else {
        response.json().then(result => {
          console.log(result)
          document.querySelector('#send_error').innerHTML = result.error;
        }).catch(() => { document.querySelector('#send_error').innerHTML = "Communication error" })
      }
    }).catch(() => { document.querySelector('#send_error').innerHTML = "Communication error" })
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Show no error
  document.querySelector('#send_error').innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name, clear emails
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      // console.log(emails);

      emails.forEach((email) => {

        const element = document.createElement('div');
        element.classList.add('email-in-list');
        if (email.read) {
          element.classList.add('email-in-list-read')
        }
        else {
          element.classList.add('email-in-list-unread')
        }
        element.innerHTML = `<h3>Subject: ${email.subject}</h3><p>From: ${email.sender}<br>To: ${email.recipients}<br>${email.timestamp}</p>`;
        element.addEventListener('click', function () {
          load_email(mailbox, email.id)
        });
        document.querySelector('#emails-view').append(element);

      })
    });

}

function update_archive(set_archive, email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: set_archive
  })
  }).then(() => load_mailbox('inbox'))
}

function load_email(mailbox, email_id) {
    // Show the mail and hide other views
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email-view').style.display = 'none';
    document.querySelector('#compose-view').style.display = 'none';


    if (mailbox !== 'sent') {
      document.getElementById("archive-button").style.display = 'block';
    } else {
      document.getElementById("archive-button").style.display = 'none';
    }

    fetch(`/emails/${email_id}`, {
      method: 'GET'
    }).then(response => response.json())
    .then(email => {
      document.getElementById("email-subject").innerHTML = email.subject;
      document.getElementById("email-from").innerHTML = email.sender;
      document.getElementById("email-to").innerHTML = email.recipients;
      document.getElementById("email-time").innerHTML = email.timestamp;
      document.getElementById("email-content").innerHTML = email.body;

      archive_button = document.getElementById("archive-button")
      if (email.archived) {
        archive_button.innerHTML = "Un-Archive"
        archive_button.onclick = () => update_archive(false, email_id)
      } else {
        archive_button.innerHTML = "Archive"
        archive_button.onclick = () => update_archive(true, email_id)
      }

      document.querySelector('#email-view').style.display = 'block';
    })

    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
    })
    })

}