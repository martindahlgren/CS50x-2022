window.addEventListener('load', function () {
  console.log("Page has loaded!")
  scroll_to_chat_end();
  update_new_msg_height();
})

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