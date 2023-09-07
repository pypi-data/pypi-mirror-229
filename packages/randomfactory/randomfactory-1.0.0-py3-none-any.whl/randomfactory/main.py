import random
import string


def generate_integer(min_val, max_val):
    return random.randrange(min_val, max_val + 1)


def generate_alphabet(min_val="A", max_val="z"):
    filtered_letters = list(
        filter(lambda x: min_val <= x <= max_val, string.ascii_letters)
    )
    return random.choice(filtered_letters)


def generate_string(n, letters=None, blank=False):
    if not letters:
        letters = string.ascii_letters + string.digits

    if blank:
        if n == 0:
            return ""
        elif n == 1:
            return random.choice(letters)
        elif n == 2:
            return random.choice(letters) + random.choice(letters)
        else:
            return (
                random.choice(letters)
                + "".join(random.choice(letters + " ") for _ in range(n - 2))
                + random.choice(letters)
            )
    else:
        return "".join(random.choice(letters) for _ in range(n))


def generate_word(n, min_val="A", max_val="z"):
    return "".join(generate_alphabet(min_val, max_val) for _ in range(n))


def generate_array(n, min_val, max_val):
    return [generate_integer(min_val, max_val) for i in range(n)]


def generate_2d_array(n, m, min_val, max_val):
    return [generate_array(m, min_val, max_val) for i in range(n)]


def generate_unique_array(n, min_val, max_val):
    return random.sample(range(min_val, max_val + 1), n)


def generate_subseq(arr, size):
    prev_idx, length, subseq = -1, len(arr), []
    for i in range(1, size + 1):
        idx = generate_integer(prev_idx + 1, length - (size - i) - 1)
        subseq.append(arr[idx])

        prev_idx = idx

    return subseq
