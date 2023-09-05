from datetime import datetime

class CommandLogs:
    def __init__(self):
        self.history = []

    def add_text(self, text):
        self.history.append((datetime.now(), text))

    def get_history(self):
        formatted_history = []
        for timestamp, text in self.history:
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            formatted_history.append(f"[{formatted_time}] {text}")
        return "\n".join(formatted_history)


def main():
    history = CommandLogs()
    
    while True:
        user_input = input("Enter text: ")
        
        if user_input == "fdr log":
            print("Text History:")
            print(history.get_history())
        else:
            history.add_text(user_input[3:])


if __name__ == "__main__":
    main()
