import logging
import threading

import customtkinter as ctk

import backend
from personalities import PERSONALITIES

logger = logging.getLogger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

app = None
chat_box = None
input_entry = None
status_label = None
buttons = []


def setup_logging():
    logging.basicConfig(
        filename="assistant.log",
        filemode="w",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.info("Logging initialized.")


def send(event=None):
    """Display the user request and the answer in the chat box."""
    user_input = input_entry.get().strip()

    if not user_input:
        return

    logger.info(f"Send button triggered with input: {user_input[:50]}...")
    disable_buttons()

    chat_box.insert("end", f"You: {user_input}\n")
    chat_box.insert("end", "Assistant: Thinking...\n")
    chat_box.see("end")

    input_entry.delete(0, "end")

    thread = threading.Thread(
        target=get_response,
        args=(user_input,),
        daemon=True,
    )
    thread.start()


def get_response(user_input):
    """Send the message to the bot and update the UI with the result."""
    try:
        logger.info(f"Requesting  response for input: {user_input[:50]}...")
        response = backend.chat_bot(user_input)
        app.after(0, finish_response, response)
    except Exception as e:
        logger.error(f"Error while getting response: {e}")
        app.after(0, finish_response, f"Error: {e}")


def finish_response(response):
    """Remove the loading message and display the final response."""
    chat_box.delete("end-2l", "end-1l")
    chat_box.insert("end", f"Assistant: {response}\n")
    chat_box.see("end")

    status = backend.get_status_summary()
    status_label.configure(
        text=f"Status: {status['model']} | Tokens: {status['tokens']} | Deleted: {status['deleted']}"
    )
    logger.info(f"Response finished: {response[:50]}...")

    enable_buttons()


def reset_chat_history():
    """Reset the chat history."""
    backend.reset_conversation()
    chat_box.delete("1.0", "end")
    chat_box.insert("end", "Assistant ,Chat History Deleted\n")
    logger.info("Chat history reset by user.")


def clear():
    """Clear the text in the input field."""
    input_entry.delete(0, "end")
    logger.info("Input field cleared.")


def clear_chat():
    """Clear the text displayed in the chat box."""
    chat_box.delete("1.0", "end")
    logger.info("Chat box cleared.")


def change_personality(choice):
    """Update the active conversation personality and reset the chat."""
    backend.set_personality(choice)
    chat_box.insert("end", f"You'v chosen {choice}, as a pernonality \n")
    logger.info(f"Personality updated in GUI: {choice}")


def disable_buttons():
    """Disable all interactive control buttons."""
    for button in buttons:
        button.configure(state="disabled")
    logger.info("Buttons disabled while waiting for response.")


def enable_buttons():
    """Re-enable all interactive control buttons."""
    for button in buttons:
        button.configure(state="normal")
    logger.info("Buttons enabled after response.")


def build_gui():
    """Create the main application window and widgets."""
    global app, chat_box, input_entry, status_label, buttons

    logger.info("Building GUI...")
    app = ctk.CTk()
    app.title("Sassy Assistant")
    app.geometry("700x700")

    chat_frame = ctk.CTkFrame(app, fg_color="#0D0512", border_width=5, corner_radius=25)
    chat_frame.pack(side="top", fill="both", expand=True)

    input_frame = ctk.CTkFrame(app, fg_color="#0D0512", border_width=5, corner_radius=25)
    input_frame.pack(side="top", fill="both", expand=True)

    status_label = ctk.CTkLabel(input_frame, text="")
    status_label.grid(row=0, column=1, columnspan=2, sticky="sew", pady=10)
    default_personality = ctk.CTkLabel(input_frame, text="Default Personnality: Sassy 😒")
    default_personality.grid(row=0, column=0, columnspan=2, sticky="sw", pady=10, padx=15)

    chat_label = ctk.CTkLabel(chat_frame, text="Multi Personnality Assistant", font=("Starlight Street", 20))

    chat_frame.columnconfigure((0, 1), weight=1, uniform="a")
    chat_frame.rowconfigure(0, weight=2, uniform="a")
    chat_frame.rowconfigure(1, weight=15, uniform="a")

    input_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="a")
    input_frame.rowconfigure(0, weight=1, uniform="a")

    chat_box = ctk.CTkTextbox(
        chat_frame,
        corner_radius=20,
        wrap="word",
        fg_color="#09040C",
        border_width=1,
        border_color="#C8BADE",
    )
    chat_box.grid(column=0, row=1, columnspan=2, sticky="nswe", ipady=30)

    input_entry = ctk.CTkEntry(
        input_frame,
        placeholder_text="How can i help you",
        fg_color="#09040C",
        corner_radius=20,
        border_color="#C8BADE",
        border_width=1,
    )
    input_entry.bind("<Return>", send)

    send_button = ctk.CTkButton(
        input_frame,
        text="Send",
        fg_color="#09040C",
        corner_radius=15,
        border_width=1,
        border_color="light gray",
        hover_color="#231D26",
        command=send,
    )
    clear_button = ctk.CTkButton(
        input_frame,
        text="clear",
        fg_color="#09040C",
        corner_radius=15,
        border_width=1,
        border_color="light gray",
        hover_color="#231D26",
        command=clear,
    )
    clear_chat_button = ctk.CTkButton(
        input_frame,
        text="clear Chat",
        fg_color="#09040C",
        corner_radius=15,
        border_width=1,
        border_color="light gray",
        hover_color="#231D26",
        command=clear_chat,
    )
    clear_chat_history_button = ctk.CTkButton(
        input_frame,
        text="Reset Conversation",
        fg_color="#09040C",
        corner_radius=15,
        border_width=1,
        border_color="light gray",
        hover_color="#231D26",
        command=reset_chat_history,
    )
    personality_menu = ctk.CTkOptionMenu(
        input_frame,
        values=list(PERSONALITIES.keys()),
        command=change_personality,
        fg_color="#09040C",
        button_color="#856D99",
        hover="disabled",
    )

    buttons = [
        send_button,
        clear_button,
        clear_chat_button,
        clear_chat_history_button,
        personality_menu,
    ]

    personality_menu.set("Sassy 😒")

    input_entry.grid(column=1, columnspan=2, row=0, sticky="ew", ipady=5, ipadx=100)
    send_button.grid(column=0, row=0, sticky="sew", pady="75", padx=5)
    clear_button.grid(column=1, row=0, sticky="sew", pady="75", padx=5)
    clear_chat_button.grid(column=2, row=0, pady="75", sticky="swe", padx=5)
    clear_chat_history_button.grid(column=3, row=0, pady="75", sticky="swe", padx=5)
    chat_label.grid(row=0, column=0, columnspan=2, sticky="wens")
    personality_menu.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    logger.info("GUI built successfully.")
    return app


def run_app():
    """Start the application."""
    logger.info("Running application.")
    build_gui()
    app.mainloop()
