import React from 'react';

const ChatbotMessageAvatar = () => {
    return (
        <div className="react-chatbot-kit-chat-bot-avatar">
            <div className="react-chatbot-kit-chat-bot-avatar-container">
                <p className="react-chatbot-kit-chat-bot-avatar-letter">B</p>
            </div>
        </div>
    );
};

function CustomChatMessage({ state, message }) {
    return (
        <>
            <div className="react-chatbot-kit-chat-bot-message-container">
                <ChatbotMessageAvatar />
                <div className="react-chatbot-kit-chat-bot-message" style={{ backgroundColor: '#376B7E' }}>
                    <div dangerouslySetInnerHTML={{ __html: message.message }}></div>
                    <div className="react-chatbot-kit-chat-bot-message-arrow" style={{ borderRightColor: '#376B7E' }}></div>
                </div>
            </div>
        </>
    )
}

export default CustomChatMessage