import requests
from bs4 import BeautifulSoup
import schedule
import time
import re
import urllib.parse

# ==========================================
# CONFIGURAÇÕES PESSOAIS (CALLMEBOT)
# ==========================================
# 1. O seu número de telefone com DDI e DDD (Ex: 5534999999999)
TELEFONE = "553499170314"

# 2. A senha (API Key) que o CallMeBot te enviou no WhatsApp
API_KEY_CALLMEBOT = "2939150"

# Produtos que queremos monitorar
PRODUTOS = [
    {
        "nome": "S24 ULTRA (Buscapé)",
        "url": "[https://www.buscape.com.br/celular/smartphone-samsung-galaxy-s24-ultra-5g-256gb-camera-quadrupla?_lc=88&searchterm=s24%20ultra](https://www.buscape.com.br/celular/smartphone-samsung-galaxy-s24-ultra-5g-256gb-camera-quadrupla?_lc=88&searchterm=s24%20ultra)",
        "preco_alvo": 4100.00,
        "site": "buscape"
    },
    {
        "nome": "S24 ULTRA (Zoom)",
        "url": "[https://www.zoom.com.br/celular/smartphone-samsung-galaxy-s24-ultra-5g-256gb-camera-quadrupla?_lc=88&searchterm=s24%20ultra](https://www.zoom.com.br/celular/smartphone-samsung-galaxy-s24-ultra-5g-256gb-camera-quadrupla?_lc=88&searchterm=s24%20ultra)",
        "preco_alvo": 4100.00,
        "site": "zoom"
    }
]

# ==========================================
# FUNÇÕES DE RASTREAMENTO E NOTIFICAÇÃO
# ==========================================


def enviar_whatsapp(mensagem):
    """Envia mensagem para o WhatsApp via CallMeBot API."""
    # A biblioteca urllib transforma espaços e caracteres especiais para o formato de URL válido
    mensagem_formatada = urllib.parse.quote(mensagem)

    url = f"[https://api.callmebot.com/whatsapp.php?phone=](https://api.callmebot.com/whatsapp.php?phone=){TELEFONE}&text={mensagem_formatada}&apikey={API_KEY_CALLMEBOT}"

    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            print("✅ Mensagem de WhatsApp enviada com sucesso (via CallMeBot)!")
        else:
            print(f"❌ Erro ao enviar WhatsApp. Status: {resposta.status_code}")
            print("Detalhes:", resposta.text)
    except Exception as e:
        print("❌ Erro na conexão com o CallMeBot:", e)


def obter_preco_html(url, site):
    """Acessa a URL e tenta extrair o preço."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    try:
        resposta = requests.get(url, headers=headers, timeout=15)
        if resposta.status_code != 200:
            print(f"Erro ao acessar {url}: Status {resposta.status_code}")
            return None

        soup = BeautifulSoup(resposta.content, 'html.parser')
        preco_texto = None

        if site in ["buscape", "zoom"]:
            # Tenta encontrar a tag principal de preço usada na B2W/Buscapé e Zoom
            elemento_preco = soup.find(attrs={"data-testid": "price-value"})
            if not elemento_preco:
                elemento_preco = soup.find(
                    "strong", class_=re.compile("Price", re.IGNORECASE))

            if elemento_preco:
                preco_texto = elemento_preco.text

        if preco_texto:
            # Limpa o texto (R$ 3.500,99 -> 3500.99)
            preco_limpo = preco_texto.replace('R$', '').replace(
                '.', '').replace(',', '.').strip()
            match = re.search(r'\d+(\.\d+)?', preco_limpo)
            if match:
                return float(preco_limpo)

        return None

    except Exception as e:
        print(f"Erro ao processar a página: {e}")
        return None

# ==========================================
# O AGENTE (LÓGICA PRINCIPAL)
# ==========================================


def rotina_de_verificacao():
    print(
        f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando verificação de preços...")

    for item in PRODUTOS:
        print(f"Buscando preço para: {item['nome']}")
        preco_atual = obter_preco_html(item['url'], item['site'])

        if preco_atual is None:
            print(
                f"⚠️ Não foi possível encontrar o preço de {item['nome']}. O layout do site pode ter mudado.")
            continue

        print(
            f"💰 Preço atual de {item['nome']}: R$ {preco_atual:.2f} (Alvo: R$ {item['preco_alvo']:.2f})")

        if preco_atual <= item['preco_alvo']:
            mensagem = (
                f"🚨 *ALERTA DE PREÇO!*\n\n"
                f"O produto *{item['nome']}* atingiu o preço alvo!\n"
                f"Preço Atual: *R$ {preco_atual:.2f}*\n"
                f"Link: {item['url']}"
            )

            enviar_whatsapp(mensagem)

            # Zera o preço alvo para não alertar repetidamente na próxima rodada
            item['preco_alvo'] = 0

# ==========================================
# AGENDAMENTO
# ==========================================


print("Iniciando o Agente Monitor de Preços (via CallMeBot)...")
rotina_de_verificacao()

# Agenda para rodar a cada 30 minutos
schedule.every(30).minutes.do(rotina_de_verificacao)

#while True:
  #  schedule.run_pending()
 #   time.sleep(1)
