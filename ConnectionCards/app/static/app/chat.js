window.addEventListener('load', function () {
  console.log("Page has loaded!")
  load_conversations();
  scroll_to_chat_end();
  update_new_msg_height();
  document.querySelector('#messages').dataset.current_conv_user_id = undefined;
  document.getElementById("send-button").disabled = true
  document.getElementById("send-button").onclick = send_message
})

function append_to_conversation(messages)
{
  messages_div = document.querySelector('#messages')

  for (const message of messages)
  {
    const container_div = document.createElement("div");
    const message_div = document.createElement("div");
    message_div.innerText = message.message;

    if (message.sent_by_me)
    {
      container_div.classList.add("my-message-container");
      message_div.classList.add("my-message");
    }
    else
    {
      container_div.classList.add("their-message-container");
      message_div.classList.add("their-message");
    }
    container_div.appendChild(message_div);
    messages_div.appendChild(container_div);
  }
  if (messages.length != 0)
  {
    scroll_to_chat_end();
  }
}

function send_message()
{
  content = document.getElementById("new-message").value
  document.getElementById("new-message").value = ""
  recipient = document.querySelector('#messages').dataset.current_conv_user_id;
  if (recipient == undefined)
  {
    return;
  }

  fetch("/send_chat", {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken },
    credentials: 'same-origin', // Do not send CSRF token to another domain.
    body: JSON.stringify({
        recipient: recipient,
        message: content
    })
  })
}

function load_conversation(name, id)
{
  document.querySelector('#current_conv_name').innerText = name;
  document.querySelector('#messages').dataset.current_conv_user_id = id;
  document.getElementById("send-button").disabled = false


  document.querySelector('#messages').innerHTML = "";

  fetch(`/get_conversation/${id}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
        append_to_conversation(data.messages)
      }
    ).catch(error => {
      console.error('Error fetching data:', error);
    });

}


function fill_conversations(data)
{
  conversations_div = document.querySelector('#chat-conversations-all');
  conversations_div.innerHTML = ""
  // Get conversations from server
  for (const conversation of data.conversations) {
    const newDiv = document.createElement("div");
    newDiv.classList.add("chat-conversation-profile")
    if (conversation.unread)
    {
      newDiv.classList.add("chat-conversation-profile-unread")
    }
    const newImg = document.createElement("img")
    newImg.src = conversation.picture
    newImg.classList.add("chat-conv-profile-pic")
    newDiv.appendChild(newImg)
    newDiv.appendChild(document.createTextNode(conversation.name))

    newDiv.onclick = () => {newDiv.classList.remove("chat-conversation-profile-unread"); load_conversation(conversation.name, conversation.user_id)}

    conversations_div.appendChild(newDiv)
  }
}


function load_conversations()
{
  // Get conversations from server

  fetch('/get_conversations')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
        fill_conversations(data)
      }
    ).catch(error => {
      console.error('Error fetching data:', error);
    });

}


function scroll_to_chat_end()
{
  messages = document.querySelector('#messages');
  if (messages)
  {
    messages.scrollTop = messages.scrollHeight;
  }
}

function update_new_msg_height()
{
  newmessage = document.querySelector('#new-message');
  newmessage.style.minheight = "";
  newmessage.style.height=0;
  newmessage.style.height = Math.max(newmessage.scrollHeight + 3) + "px"
}