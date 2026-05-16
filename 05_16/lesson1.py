import random


def play_guessing_game():
    """Play a number guessing game between 1 and 100."""
    secret_number = random.randint(1, 100)
    attempts = 0

    print("歡迎來到猜數字遊戲！")
    print("我已經想好一個 1 到 100 之間的整數，來猜看看吧！")
    print("輸入 q 或 quit 可以提前結束遊戲。\n")

    while True:
        user_input = input("請輸入你的猜測：").strip()
        if user_input.lower() in {"q", "quit"}:
            print(f"遊戲結束，正確答案是 {secret_number}。")
            break

        if not user_input.isdigit():
            print("請輸入一個有效的整數，或輸入 q 結束。")
            continue

        guess = int(user_input)
        attempts += 1

        if guess < secret_number:
            print("太小了！再試一次。\n")
        elif guess > secret_number:
            print("太大了！再試一次。\n")
        else:
            print(f"恭喜你猜對了！答案就是 {secret_number}。")
            print(f"你總共猜了 {attempts} 次。\n")
            break


if __name__ == "__main__":
    play_guessing_game()
    print("遊戲結束，謝謝你的參與！")

