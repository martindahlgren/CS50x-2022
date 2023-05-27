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
        if (element.read) {
          element.classList.add('email-in-list-read')
        }
        else {
          element.classList.add('email-in-list-unread')
        }
        element.innerHTML = `<h3>Subject: ${email.subject}</h3><p>From: ${email.sender}<br>To: ${email.recipients}<br>${email.timestamp}</p>`;
        element.addEventListener('click', function () {
          console.log('This element has been clicked!')
        });
        document.querySelector('#emails-view').append(element);

      })
    });

}