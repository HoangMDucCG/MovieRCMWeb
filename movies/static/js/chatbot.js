document.addEventListener("DOMContentLoaded", function () {
    const chatToggle = document.getElementById("ai-chat-toggle");
    const chatWindow = document.getElementById("ai-chat-window");
    const closeBtn = document.getElementById("close-chat-btn");
    const sendBtn = document.getElementById("send-chat-btn");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");

    // Ẩn/hiện khung chat
    chatToggle.addEventListener("click", () => {
        chatWindow.style.display = chatWindow.style.display === "none" ? "flex" : "none";
    });
    closeBtn.addEventListener("click", () => chatWindow.style.display = "none");

// Hàm gắn tin nhắn lên màn hình
    function appendMessage(text, sender) {
        const msgDiv = document.createElement("div");
        
        // Nếu là bot (AI) thì thêm class ai-format, nếu là user thì giữ nguyên
        msgDiv.className = `msg ${sender === "user" ? "user-msg" : "bot-msg ai-format"}`;
        
        msgDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; 
    }

    // Lấy CSRF Token để không bị Django block request POST
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

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        appendMessage(text, "user");
        chatInput.value = "";

        // Hiển thị trạng thái đang nhập
        const loadingId = "loading-" + Date.now();
        const loadingDiv = document.createElement("div");
        loadingDiv.className = "msg bot-msg";
        loadingDiv.id = loadingId;
        loadingDiv.innerHTML = "<em>Trợ lý đang tìm phim...</em>";
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch("/api/chatbot/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken") 
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            document.getElementById(loadingId).remove();
            appendMessage(data.reply, "bot");

        } catch (error) {
            document.getElementById(loadingId).remove();
            appendMessage("Lỗi kết nối, vui lòng thử lại!", "bot");
        }
    }

    sendBtn.addEventListener("click", sendMessage);
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
});