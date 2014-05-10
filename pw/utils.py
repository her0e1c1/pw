

def ask_yes_or_no(prompt="yes or no"):
    ans = raw_input(prompt)
    if ans.lower() in ("y", "yes", "1", "true", "t"):
        return True
    else:
        return False
