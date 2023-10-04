import React, { useState } from 'react';
import Chatbot from 'react-chatbot-kit'
import { createChatBotMessage, createCustomMessage } from 'react-chatbot-kit';
import 'react-chatbot-kit/build/main.css';
import './CustomChatBot.css';
import CustomChatMessage from './CustomChatMessage';

function CustomChatBot({ msgHandler }) {

    const botName = "PaloozaBot";

    const config = {
        initialMessages: [createChatBotMessage(`Hi! I'm ${botName}`)],
        botName: botName,
        customStyles: {
            botMessageBox: {
                backgroundColor: '#376B7E',
            },
            chatButton: {
                backgroundColor: '#5ccc9d',
            },
        },
        customMessages: {
            customhtml: (props) => {
                return <CustomChatMessage {...props} message={props.state.messages.find(msg => (msg.payload === props.payload))}/>
            }
        }
    };

    const ActionProvider = ({ createChatBotMessage, setState, children }) => {
        const handleChat = async (msg) => {
            const response = await msgHandler(msg);
            const botMessage = createCustomMessage(response, "customhtml", {payload: response});

            setState((prev) => ({
                ...prev,
                messages: [...prev.messages, botMessage]
            }));
        }
        return (
            <div>
                {React.Children.map(children, (child) => {
                    return React.cloneElement(child, {
                        actions: {
                            handleChat
                        },
                    });
                })}
            </div>
        );
    };

    const MessageParser = ({ children, actions }) => {
        const parse = (message) => {
            actions.handleChat(message);
        };

        return (
            <div>
                {React.Children.map(children, (child) => {
                    return React.cloneElement(child, {
                        parse: parse,
                        actions: actions,
                    });
                })}
            </div>
        );
    };

    return (
        <Chatbot
            config={config}
            messageParser={MessageParser}
            actionProvider={ActionProvider}
        />
    )
}

export default CustomChatBot