from datetime import datetime
import pandas as pd
import http.client
import requests
import base64
import json
import time
import os
import logging

logging.basicConfig(filename=r'logs\script_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

logging.info("Início do script")

ARQUIVO = 'estoque_code_refresh_tokenur.txt'
ARQUIVO_TOKEN = 'estoque_code_token.txt'
CLIENT_ID = 'client_id.txt'
CLEINT_SECRET = 'client_secret.txt'

def send_message(token, chat_id, msg):
        try:
            data = {"chat_id": chat_id, "text": msg}
            url = "https://api.telegram.org/bot{}/sendMessage".format(token)
            requests.post(url, data)
        except Exception as e:
            print("Erro no sendMessage:", e)

def ajustar_ean(ean):
    return str(int(ean)).rjust(13, '0')

def gerar_credenciais_base64(client_id, client_secret):
    """
    Gera a string de credenciais no formato Base64 a partir do client_id e client_secret.
    """
    credentials = f"{client_id}:{client_secret}"
    return base64.b64encode(credentials.encode()).decode()

def refresh_token(token, client_id, client_secret):
    """
    Realiza a renovação do token OAuth com o Bling.
    """
    url = "https://www.bling.com.br/Api/v3/oauth/token"

    # Gera as credenciais em Base64
    credentials_base64 = gerar_credenciais_base64(client_id, client_secret)

    # Cabeçalhos da solicitação
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "1.0",
        "Authorization": f"Basic {credentials_base64}"
    }

    # Corpo da solicitação
    data = {
        "grant_type": "refresh_token",
        "refresh_token": token
    }

    # Fazendo a solicitação POST
    response = requests.post(url, headers=headers, data=data)

    # Verifica se a resposta foi bem-sucedida
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.json()}
    
automacao = '5495104211:AAHJIrse-testet'

code_refresh_token_txt = ""
code_token = ""
client_id = ""
client_secret = ""

# Loop contínuo para verificar alterações
while True:
    if os.path.exists(fr'{ARQUIVO}'):
        with open(fr'{ARQUIVO}', 'r') as f:
            code_refresh_token_txt = f.read()

    if os.path.exists(fr'{CLIENT_ID}'):
        with open(fr'{CLIENT_ID}', 'r') as f:
            client_id = f.read()

    if os.path.exists(fr'{CLEINT_SECRET}'):
        with open(fr'{CLEINT_SECRET}', 'r') as f:
            client_secret = f.read()

    print(" ")
    print("Codigo antigo - ", code_refresh_token_txt)
    print(" ")
    print("Codigo client_id - ", client_id)
    print(" ")
    print("Codigo client_secret - ", client_secret)

    # Obtém a data e hora atual
    data_hora_atual = datetime.now()

    # Atualiza o token
    token = code_refresh_token_txt
    resultado = refresh_token(token, client_id, client_secret)
    code_token = resultado.get("access_token", "")

    if "refresh_token" in resultado:
        code_refresh_token = resultado["refresh_token"]
        with open(fr'{ARQUIVO}', 'w+') as f:
            f.write(str(code_refresh_token))

    # Carrega os dados do estoque atual
    df_produtos_jk = pd.read_excel(r'ultimo_saldos_estoque.xlsx')
    ultimo_saldos_estoque = df_produtos_jk.to_dict('records')

    # Consulta API da DAG
    body = {
        "chave": "teste",
        "cgc": "teste",
        "tag": "produto",
        "data_update": "teste",
        "filtro": [
            {
                "produto": {
                    "codigo_subgrupo": "",
                    "ean": "",
                    "descricao_produto": "",
                    "lista_produto": [],
                    "status": "EM LINHA, SAINDO DE LINHA"
                }
            }
        ]
    }

    json_data = json.dumps(body)
    headers = {"Content-Type": "application/json",
               "Authorization": "Basic cHJvamV0b01hbW9laXettesteAbWFtb2UyMDIw"}
    conndag = http.client.HTTPSConnection("api-b2b.guarany.com.br")
    conndag.request("POST", "/syncProduto", json_data, headers)
    response = conndag.getresponse()
    print("CONECTOU NA API DA DAG - ", response.status, response.reason)
    datadag = json.loads(response.read())
    conndag.close()

    lista_produtos_DAG = []
    for produto in datadag.get("produto", []):
        estoque_atualizado = {
            "sku": "FOR" + produto["sku"],
            "ean": str(produto["ean"]).rjust(13, '0'),
            "descricaoFornecedor": produto["titulo_do_produto"],
            "descricao_longa": produto["descricao_longa"],
            "marca_fabricante": produto["marca_fabricante"],
            "descr_segmento": produto["descr_segmento"],
            "estoque": produto["estoque"],
            "precocusto": produto["valor_custo"]}
        lista_produtos_DAG.append(estoque_atualizado)

    # Ajuste de estoque conforme critérios
    for dag in lista_produtos_DAG:
        if dag['estoque'] > 200:
            dag['estoque'] = 200
        if dag['estoque'] <= 20:
            dag['estoque'] = 0

    produtos_para_zera_estoque_df = pd.read_excel(r'produtos_para_zera_estoque.xlsx')
    produtos_para_zera_estoque = produtos_para_zera_estoque_df.to_dict('records')
    for tem in lista_produtos_DAG:
        for zera in produtos_para_zera_estoque:
            if str(f"{zera['EAN']}").rjust(13, '0') in tem['ean']:
                tem['estoque'] = 0

    for tem in lista_produtos_DAG:
        if ('0451-DANONE' == tem['marca_fabricante'] or '0459-DIASIP' == tem['marca_fabricante']) and \
           ('LATICINIOS' in tem['descr_segmento'] or 'NUTRICAO ESPECIALIZ ADULTO' in tem['descr_segmento'] or 'NUTRICAO ESPECIALIZ INFANTIL' in tem['descr_segmento']):
            tem['estoqueAtual'] = 0

    # Atualização do estoque
    ultimo_saldos_estoque_atualizado = []
    for produto_dag in lista_produtos_DAG:
        for i, produto_ultimo in enumerate(ultimo_saldos_estoque):
            if ajustar_ean(produto_dag["ean"]) == ajustar_ean(produto_ultimo["ean"]):
                if produto_dag['estoque'] != produto_ultimo['estoque']:
                    print("Entrou.......................................", ajustar_ean(produto_dag["ean"]))
                    ultimo_saldos_estoque[i]['estoque'] = produto_dag['estoque']
                    ultimo_saldos_estoque[i]['precounitario'] = produto_dag['precocusto']
                    ultimo_saldos_estoque[i]['precocusto'] = produto_dag['precocusto']
                    ultimo_saldos_estoque[i]['data'] = data_hora_atual
                    ultimo_saldos_estoque_atualizado.append(produto_ultimo)

    if len(ultimo_saldos_estoque_atualizado) <= 0:
        print("Nenhuma alteração detectada. Fechando o terminal e reiniciando em 1 hora...")
        msg1 = 'JK CE - ESTOQUE - Nenhuma alteração detectada. Fechando o terminal e reiniciando em 1 hora...'
        send_message(automacao, 'id_codigo', msg1)
        time.sleep(3600)  # Aguarda 1 hora antes de reexecutar o código


    # Salva os dados atualizados
    df_produtos_alterados = pd.DataFrame.from_dict(ultimo_saldos_estoque_atualizado)
    df_produtos_alterados.to_excel(r'ultimo_saldos_estoque_atualizado.xlsx', index=False)
    print("Arquivo atualizado salvo com sucesso.")

    df_produtos_atualizados = pd.DataFrame.from_dict(ultimo_saldos_estoque)
    df_produtos_atualizados.to_excel(r'ultimo_saldos_estoque.xlsx', index=False)
    print("Arquivo geral atualizado salvo com sucesso.") 

    # Atualiza o estoque na API Bling
    if len(ultimo_saldos_estoque_atualizado) > 0:
        for produtoAlterado in ultimo_saldos_estoque_atualizado:
            connAlterado = http.client.HTTPSConnection("api.bling.com.br")
            payload = json.dumps({
                "deposito": {
                    "id": 11843916782
                },
                "operacao": "B",
                "produto": {
                    "id": produtoAlterado['idproduto'],
                    "codigo": produtoAlterado['sku']
                },
                "quantidade": float(produtoAlterado['estoque']),
                "preco": float(produtoAlterado['precounitario']),
                "custo": float(produtoAlterado['precocusto']),
                "observacoes": "ATUALIZAÇÃO VIA API TABOSA"
            })
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {code_token}',
                'Cookie': 'PHPSESSID=ljtd0gofg66sfeaugk82hj9rbi'
            }
            connAlterado.request("POST", "/Api/v3/estoques", payload, headers)
            resAlterado = connAlterado.getresponse()
            dataAlterado = resAlterado.read()
            print(dataAlterado.decode("utf-8"))
            print("Foi esse que atualizou pow - ", produtoAlterado['sku'])
            time.sleep(0.5)

        # Fechando o terminal e reiniciando em 1 hora
        print("Alteração detectada. Fechando o terminal e reiniciando em 1 hora...")
        msg2 = 'JK CE - ESTOQUE - Alteração detectada. Fechando o terminal e reiniciando em 1 hora...'
        send_message(automacao, '830463079', msg2)
        time.sleep(3600)


    logging.info("Fim do script")