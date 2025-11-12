document.addEventListener('DOMContentLoaded', () => {
    const chatbotForm = document.getElementById('chatbot-form');
    const userInput = document.getElementById('user-input');
    const chatbotMessages = document.getElementById('chatbot-messages');
    const sendBtn = document.getElementById('send-btn');

    // --- DÉBUT DE LA LOGIQUE DU CHATBOT ---

    // 1. Définissez votre System Prompt (le cadre du modèle)
    const systemPrompt = `
<persona>
Tu es Jackbot, un assistant virtuel expert de l'administration française. Ta seule et unique fonction est de fournir des informations factuelles et vérifiables.
</persona>

<mission_principale>
Guider les utilisateurs à travers les démarches administratives françaises en citant des textes de loi, des décrets, et des pages de sites gouvernementaux officiels.
</mission_principale>

<directives_strictes>
    <règle id="1">
    **Neutralité et objectivité** : Ne jamais exprimer d'opinions, de sentiments ou de jugements. Ne jamais aborder la politique, la religion ou tout autre sujet controversé. Tu es un transmetteur d'information, pas un commentateur.
    </règle>
    
    <règle id="2">
    **Citation des sources obligatoire** : Chaque information factuelle doit être accompagnée de sa source. Si aucune source n'est disponible, tu dois appliquer la règle 4.
    Format de citation : "[Source : Type de source - Référence]".
    Exemple : "[Source : Code du Travail - Article L1225-16]" ou "[Source : site service-public.fr - page 'Demander un passeport']".
    </règle>
    
    <règle id="3">
    **Gestion du hors-sujet** : Si l'utilisateur tente de discuter de sujets non administratifs, tu dois poliment mais fermement recentrer la conversation.
    Exemple de réponse : "Je vous remercie pour cet échange. Ma mission est de vous assister sur les questions administratives. Avez-vous une question à ce sujet ?".
    </règle>

    <règle id="4">
    **Reconnaissance de l'ignorance** : Si une question est trop complexe, trop spécifique, ou sort de ta base de connaissances, tu dois obligatoirement répondre : "Cette question dépasse mon champ de compétences. Pour garantir une réponse fiable, il est préférable de contacter directement l'organisme compétent ou un conseiller juridique." N'essaie JAMAIS d'inventer une réponse.
    </règle>
</directives_strictes>

<exemple_interaction>
    <utilisateur>Salut Jackbot, comment ça va aujourd'hui ?</utilisateur>
    <jackbot>Bonjour, je suis opérationnel et prêt à vous aider. En quoi puis-je vous assister concernant l'administration française ?</jackbot>
    
    <utilisateur>Je veux savoir combien de jours de congé paternité j'ai.</utilisateur>
    <jackbot>La durée du congé de paternité et d'accueil de l'enfant est fixée à 25 jours calendaires. [Source : Code du Travail - Article L1225-35]. Pour plus de détails, vous pouvez consulter la page dédiée sur le site du service public.</jackbot>
</exemple_interaction>
`;
    // 2. Initialisez l'historique de la conversation avec le system prompt
    let conversationHistory = [
        {
            role: 'system',
            content: systemPrompt,
        }
    ];

    // 3. La fonction qui appelle l'API Ollama (version améliorée)
        async function getBotResponse(userMessage) {
        // Ajoute le message de l'utilisateur à l'historique local
        conversationHistory.push({ role: 'user', content: userMessage });

        // URL correcte qui passe par Nginx vers notre nouvel endpoint
        const API_RAG_URL = "/api/ask-jackbot";

        const res = await fetch(API_RAG_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: userMessage,
                system_prompt: systemPrompt // On envoie le prompt système avec la question
            })
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || `HTTP ${res.status}`);
        }

        const data = await res.json();

        // Ajoute la réponse du bot à l'historique local
        if (data.response) {
            conversationHistory.push({ role: 'bot', content: data.response });
            return data.response;
        } else {
            // S'il y a un problème, on retire le dernier message utilisateur
            conversationHistory.pop();
            return "Désolé, une erreur est survenue lors de la génération de la réponse.";
        }
    }


    // --- LE RESTE DU CODE (AFFICHAGE) RESTE INCHANGÉ ---

    function timeNow() {
        const d = new Date();
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function appendMessage(text, role = 'bot') {
        const container = document.createElement('div');
        container.classList.add('message', role === 'user' ? 'user' : 'bot');
        const avatar = document.createElement('div');
        avatar.className = 'avatar';
        if (role === 'user') {
            const img = document.createElement('img');
            img.src = './pictures/logouserspeaking.png';
            img.alt = 'User'; img.style.width = '100%'; img.style.height = '100%'; img.style.objectFit = 'cover';
            avatar.appendChild(img);
        } else {
            const img = document.createElement('img');
            img.src = './pictures/logochatbot.png';
            img.alt = 'Bot'; img.style.width = '100%'; img.style.height = '100%'; img.style.objectFit = 'cover';
            avatar.appendChild(img);
        }
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        const content = document.createElement('div');
        content.className = 'text';
        content.textContent = text;
        const meta = document.createElement('div');
        meta.className = 'meta';
        meta.textContent = timeNow();
        bubble.appendChild(content);
        bubble.appendChild(meta);
        container.appendChild(avatar);
        container.appendChild(bubble);
        chatbotMessages.appendChild(container);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        return container;
    }

    function showTyping() {
        const el = document.createElement('div');
        el.id = 'typing-indicator';
        el.className = 'message bot';
        el.innerHTML = '<div class="avatar"></div><div class="bubble"><div class="text">...</div></div>';
        chatbotMessages.appendChild(el);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }
    function hideTyping() { const el = document.getElementById('typing-indicator'); if (el) el.remove(); }

    async function sendMessage(raw) {
        const text = raw.trim();
        if (!text) return;
        appendMessage(text, 'user');
        userInput.value = '';
        showTyping();
        try {
            const botResp = await getBotResponse(text);
            hideTyping();
            appendMessage(botResp, 'bot');
        } catch (err) {
            hideTyping();
            appendMessage('Sorry, an error occurred. Please try again later.', 'bot');
            console.error('API error:', err);
        }
    }

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(userInput.value);
        }
    });
    sendBtn.addEventListener('click', () => sendMessage(userInput.value));
    chatbotForm.addEventListener('submit', (e) => { e.preventDefault(); sendMessage(userInput.value); });
});