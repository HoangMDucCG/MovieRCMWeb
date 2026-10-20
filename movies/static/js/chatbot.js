document.addEventListener("DOMContentLoaded", function () {
    const chatToggle = document.getElementById("ai-chat-toggle");
    const chatWindow = document.getElementById("ai-chat-window");
    const closeChatBtn = document.getElementById("close-chat-btn");
    const chatMessages = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-chat-btn");

    let chatHistory = JSON.parse(sessionStorage.getItem("webphimmoi_chat_history")) || [];

    function formatBotMessage(text) {
        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong class="movie-highlight">$1</strong>');
        formatted = formatted.replace(/\n/g, '<br>');
        return formatted;
    }

    function renderHistory() {
        chatMessages.innerHTML = "";
        
        if (chatHistory.length === 0) {
            chatMessages.innerHTML = `<div class="msg bot-msg">Chào Bạn! Bạn đang muốn tìm phim thể loại gì, hay phim hợp với tâm trạng hôm nay? Mình gợi ý cho!</div>`;
        } else {
            chatHistory.forEach(msg => {
                const msgDiv = document.createElement("div");
                msgDiv.className = `msg ${msg.role === "user" ? "user-msg" : "bot-msg ai-format"}`;
                
                if (msg.role === "bot") {
                    msgDiv.innerHTML = formatBotMessage(msg.content);
                } else {
                    msgDiv.textContent = msg.content;
                }
                
                chatMessages.appendChild(msgDiv);
            });
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    renderHistory();

    chatToggle.addEventListener("click", () => {
        chatWindow.style.display = "flex";
        chatMessages.scrollTop = chatMessages.scrollHeight; 
    });
    closeChatBtn.addEventListener("click", () => chatWindow.style.display = "none");

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessageToUI("user", text);
        chatHistory.push({ role: "user", content: text });
        sessionStorage.setItem("webphimmoi_chat_history", JSON.stringify(chatHistory));
        chatInput.value = "";

        const loadingId = "loading-" + Date.now();
        chatMessages.insertAdjacentHTML('beforeend', `<div id="${loadingId}" class="msg bot-msg">Đang suy nghĩ...</div>`);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        fetch("/api/chatbot/", { 
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken") 
            },
            body: JSON.stringify({ 
                message: text,
                history: chatHistory 
            })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById(loadingId).remove();
            
            addMessageToUI("bot", data.reply);
            chatHistory.push({ role: "bot", content: data.reply });
            sessionStorage.setItem("webphimmoi_chat_history", JSON.stringify(chatHistory));
        })
        .catch(err => {
            const loadingElement = document.getElementById(loadingId);
            if(loadingElement) loadingElement.textContent = "Lỗi kết nối máy chủ!";
            console.error("Chat API Error:", err);
        });
    }

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendMessage(); });

    function addMessageToUI(role, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `msg ${role === "user" ? "user-msg" : "bot-msg ai-format"}`;
        
        // ĐÃ SỬA: Gọi hàm formatBotMessage ở đây
        if (role === "bot") {
            msgDiv.innerHTML = formatBotMessage(text);
        } else {
             msgDiv.textContent = text;
        }

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});