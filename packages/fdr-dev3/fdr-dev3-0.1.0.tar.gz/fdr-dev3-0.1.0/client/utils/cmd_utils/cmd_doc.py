import tkinter as tk
from tkinter import scrolledtext
from tkinter import PhotoImage

def fdr_documentation():
    command_descriptions = {
        "fdr pull": "Description\n...",
        "fdr push": "Description\n...",
        "fdr show": "Description\n...",
        "fdr doc": "Description\n...",
        "fdr clear": "Description\n...",
        "fdr quit": "Description\n...",
        "fdr log": "Description\n...",
    }

    def show_command_info(command):
        for label in command_labels:
            label.config(bg="SystemButtonFace")  # Reset background color for all labels
        info_text.config(state=tk.NORMAL)  # Make the text widget editable
        info_text.delete(1.0, tk.END)
        info_text.insert(tk.END, f"Command  ---> [ fdr{command[3:]} ]\n\n")
        info_text.insert(tk.END, command_descriptions.get(command, "No documentation available for this command."))
        selected_label = command_labels[commands.index(command)]
        selected_label.config(bg="lightblue")  # Highlight the selected label
        info_text.config(state=tk.DISABLED)  # Disable the text widget to prevent editing

    # Create the main window
    root = tk.Tk()
    root.title("FaradAI Documentation")

    # Create a frame for the command list on the left
    list_frame = tk.Frame(root)
    list_frame.pack(side=tk.LEFT, anchor=tk.N, padx=10, pady=10)

    # List of commands
    commands = ["fdr pull", "fdr push", "fdr show", "fdr doc", "fdr clear", "fdr quit", "fdr log"]

    # Create clickable labels for commands
    command_labels = []
    for command in commands:
        label = tk.Label(list_frame, text=command, cursor="hand2", font=("Times New Roman", 11, "underline"))
        label.pack(anchor=tk.W, pady=(5, 0))
        label.bind("<Button-1>", lambda event, cmd=command: show_command_info(cmd))
        command_labels.append(label)

    # Create a scrolled text widget to display documentation
    info_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=20, font=("Times New Roman", 11))
    info_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
    info_text.config(state=tk.DISABLED)  # Set the text widget to be non-editable
    info_text.config(bg="lightblue", padx=10, pady=10)  # Set yellow background and padding

    # Start GUI window at "fdr pull"
    show_command_info("fdr pull")

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    fdr_documentation()
