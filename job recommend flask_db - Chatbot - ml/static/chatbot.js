const chatIcon =
document.getElementById("chatIcon");

const chatContainer =
document.getElementById("chatContainer");

const closeChat =
document.getElementById("closeChat");

const maximizeChat =
document.getElementById("maximizeChat");

const chatBody =
document.getElementById("chatBody");

const userInput =
document.getElementById("userInput");

// OPEN CHAT

chatIcon.onclick = () => {

    chatContainer.style.display = "flex";

    chatIcon.style.display = "none";
};

// CLOSE CHAT

closeChat.onclick = () => {

    chatContainer.style.display = "none";

    chatIcon.style.display = "flex";
};

// =========================================
// MAXIMIZE CHAT
// =========================================

maximizeChat.onclick = () => {

    chatContainer.classList.toggle(
        "chat-maximized"
    );
};

function sendSuggestion(text) {

    userInput.value = text;

    sendMessage();
}

// SEND MESSAGE

async function sendMessage() {

    const message =
    userInput.value.trim();

    if (message === "") return;

    // USER MESSAGE

    chatBody.innerHTML += `

        <div class="user-message">

            ${message}

        </div>

    `;

    userInput.value = "";

    // FETCH BOT RESPONSE

    const response = await fetch("/chat", {

        method: "POST",

        headers: {

            "Content-Type":
            "application/json"
        },

        body: JSON.stringify({

            message: message
        })
    });

    const data =
    await response.json();

    // BOT RESPONSE

    chatBody.innerHTML += `

        <div class="bot-message">

            ${data.reply}

        </div>

    `;

    // AUTO SCROLL

    chatBody.scrollTop =
    chatBody.scrollHeight;
}
// =========================================
// ENTER KEY SEND MESSAGE
// =========================================

userInput.addEventListener("keypress", function(event) {

    if (event.key === "Enter") {

        event.preventDefault();

        sendMessage();
    }
});