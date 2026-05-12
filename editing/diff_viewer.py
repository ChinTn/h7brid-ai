import difflib



def show_diff(old_content, new_content, filename):

    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=f"OLD/{filename}",
        tofile=f"NEW/{filename}",
        lineterm=""
    )

    print("\n========== DIFF ==========\n")

    for line in diff:
        print(line)