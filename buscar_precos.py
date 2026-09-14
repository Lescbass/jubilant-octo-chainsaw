import requests
from bs4 import BeautifulSoup
import time
import re
import csv
from difflib import SequenceMatcher

BASE = "https://mobile.comprasparaguai.com.br"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; PesquisaPrecos/1.0)"}

# Edite esta lista com até 10 produtos
PRODUTOS = [
    "Perfume Lattafa Afeef Eau de Parfum Unissex 100ML",
    "Perfume Lattafa Niche Emarati Khanjar Eau de Parfum Unissex 85ML",
    "Perfume Lattafa Emaan Eau de Parfum Feminino 100ML",
    "Perfume Zimaya Roses Are White Eau de Parfum Unissex 100ML",
    "Zimaya Rose Of Dreams Edp Fem 100ML",
]

def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def buscar_produto(nome):
    url = f"{BASE}/busca/"
    r = requests.get(url, params={"q": nome}, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    candidatos = []
    for a in soup.select("a[href*='_'][href$='/']"):
        href = a.get("href", "")
        titulo = a.get("title") or a.get_text(strip=True)
        if not titulo or "/lojas/" in href or "/marcas/" in href:
            continue
        if re.search(r"_\d+/?$", href) or "__" in href:
            link = href if href.startswith("http") else BASE + href
            candidatos.append((titulo, link))

    if not candidatos:
        return None, None

    melhor = max(candidatos, key=lambda c: similaridade(c[0], nome))
    return melhor  # (titulo, link)

def extrair_ofertas(url_produto):
    r = requests.get(url_produto, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    texto = soup.get_text("\n")

    ofertas = []
    blocos = re.split(r"\n(?=US\$\s?[\d.,]+)", texto)
    for bloco in blocos:
        m_preco = re.search(r"US\$\s?([\d.,]+)", bloco)
        if not m_preco:
            continue
        preco_str = m_preco.group(1).replace(".", "").replace(",", ".")
        try:
            preco = float(preco_str)
        except ValueError:
            continue
        # tenta achar o nome da loja perto do preço
        m_loja = re.search(r"\[([A-Za-zÀ-ÿ0-9 &]+)\]\(http", bloco)
        loja = m_loja.group(1) if m_loja else "Loja não identificada"
        ofertas.append((loja.strip(), preco))

    return ofertas

def main():
    resultados = []
    for nome in PRODUTOS[:10]:
        print(f"Buscando: {nome}")
        titulo, link = buscar_produto(nome)
        if not link:
            resultados.append((nome, "NÃO ENCONTRADO", None, None))
            continue

        ofertas = extrair_ofertas(link)
        if not ofertas:
            resultados.append((nome, titulo, "sem ofertas extraídas", link))
        else:
            loja, preco = min(ofertas, key=lambda o: o[1])
            resultados.append((nome, titulo, f"US$ {preco:.2f} - {loja}", link))

        time.sleep(2)  # respeita o servidor, evita bloqueio

    with open("resultado_precos.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Produto buscado", "Produto encontrado", "Melhor preço/loja", "Link"])
        writer.writerows(resultados)

    print("\n=== RESULTADO ===")
    for linha in resultados:
        print(linha)

if __name__ == "__main__":
    main()
