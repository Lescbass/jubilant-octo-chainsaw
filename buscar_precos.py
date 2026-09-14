import requests

BASE = "https://mobile.comprasparaguai.com.br"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

PRODUTOS = [
    "Perfume Lattafa Afeef Eau de Parfum Unissex 100ML",
]

def diagnostico(nome):
    url = f"{BASE}/busca/"
    r = requests.get(url, params={"q": nome}, headers=HEADERS, timeout=20)
    print("STATUS CODE:", r.status_code)
    print("TAMANHO DA RESPOSTA:", len(r.text))
    print("PRIMEIROS 500 CARACTERES:")
    print(r.text[:500])
    print("---")
    print("CONTÉM 'Cloudflare'?", "cloudflare" in r.text.lower())
    print("CONTÉM 'captcha'?", "captcha" in r.text.lower())
    print("CONTÉM 'Lattafa'?", "lattafa" in r.text.lower())

if __name__ == "__main__":
    for nome in PRODUTOS:
        diagnostico(nome)
