from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout

while True:
    with patch_stdout():
        print("This is a debug message")
    user_input = prompt("Enter something: ")
    with patch_stdout():
        print(f"You typed: {user_input}")
    if user_input.lower() == "exit":
        break
