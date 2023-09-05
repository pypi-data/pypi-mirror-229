import httpx


def validate(url):
    try:
        httpx.URL(url)
        return True
    except httpx.InvalidURL:
        return False


a = [
    "http://www.google.com",
    "https://www.google.com",
]

for i in a:
    print(validate(i))
