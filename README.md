# Projeto: JK CE Estoque

## Descrição

Este projeto automatiza a sincronização de estoque entre sistemas internos e a API do Bling, utilizando Python. Ele realiza a atualização do estoque em tempo real, processando os dados recebidos de uma API externa e ajustando os valores conforme regras pré-definidas. Além disso, ele envia notificações via Telegram sobre o status do processo.

A aplicação é configurada para rodar em um contêiner Docker com a imagem nomeada como `jk_ce_estoque` e o contêiner chamado `jk_ce_estoque`.

---

## Funcionalidades

1. **Renovação de Tokens OAuth**: Atualiza automaticamente os tokens de acesso e de atualização necessários para acessar a API do Bling.
2. **Processamento de Estoque**:
   - Lê dados de estoque de arquivos locais.
   - Consulta informações de produtos em uma API externa (DAG).
   - Ajusta o estoque conforme regras predefinidas (e.g., limite de estoque máximo e mínimo).
   - Atualiza o estoque e os valores de custo na API do Bling.
3. **Notificações via Telegram**: Envia mensagens automáticas para um chat configurado, informando o status do processo.
4. **Geração de Logs**: Registra logs detalhados para auditoria e solução de problemas.

---

## Estrutura do Projeto

- \`\`: Arquivo que armazena o refresh token do Bling.
- \`\`: Arquivo que armazena o access token do Bling.
- \`\`: Arquivo contendo o client ID para autenticação.
- \`\`: Arquivo contendo o client secret para autenticação.
- \`\`: Planilha com os dados do estoque atual.
- \`\`: Planilha com produtos que devem ter o estoque zerado.
- **Logs**: Os logs do script são gerados no arquivo `logs\script_log.txt`.

---

## Requisitos

- Python 3.7+
- Docker
- Bibliotecas Python:
  - `pandas`
  - `requests`
  - `base64`
  - `json`
  - `http.client`
  - `logging`

---

## Configuração

### 1. Configuração do Ambiente

Certifique-se de que os seguintes arquivos estejam configurados no diretório do projeto:

- `estoque_code_refresh_tokenur.txt`: Coloque o refresh token inicial do Bling.
- `client_id.txt`: Insira o client ID fornecido pela API do Bling.
- `client_secret.txt`: Insira o client secret fornecido pela API do Bling.

### 2. Configuração do Docker

Crie o contêiner Docker com a seguinte imagem:

```bash
# Construir a imagem Docker
docker build -t jk_ce_estoque .

# Executar o contêiner
docker run --name jk_ce_estoque -v $(pwd)/logs:/app/logs -d jk_ce_estoque
```

Certifique-se de que o diretório `logs` esteja acessível para persistência dos logs.

---

## Uso

### Execução Manual

Se não estiver utilizando Docker, execute o script diretamente com Python:

```bash
python script.py
```

### Funcionalidades Automatizadas

- O script verifica atualizações de estoque continuamente.
- Notifica alterações ou status via Telegram.
- Reinicia automaticamente após um intervalo de 1 hora.

---

## Explicação do Código

### Principais Funções

#### `send_message(token, chat_id, msg)`

Envia mensagens para um chat no Telegram.

- **Parâmetros**:
  - `token`: Token do bot Telegram.
  - `chat_id`: ID do chat para envio da mensagem.
  - `msg`: Mensagem a ser enviada.

#### `ajustar_ean(ean)`

Ajusta o código EAN para ter 13 dígitos.

#### `gerar_credenciais_base64(client_id, client_secret)`

Gera credenciais codificadas em Base64 para autenticação.

#### `refresh_token(token, client_id, client_secret)`

Renova o token de acesso à API do Bling.

#### Processamento de Estoque

1. **Carregamento de Dados**:
   - Lê os dados do arquivo `ultimo_saldos_estoque.xlsx`.
2. **Consulta à API DAG**:
   - Recupera informações atualizadas de estoque.
3. **Ajustes**:
   - Aplica limites de estoque.
   - Zera estoque de produtos conforme regras predefinidas.
4. **Atualização**:
   - Atualiza o estoque na API do Bling.
   - Salva os resultados nos arquivos locais.

### Controle do Fluxo

- **Loop Contínuo**: O script executa em um loop infinito, pausando por 1 hora após cada execução.
- **Logs**: Registra o início, fim e eventos relevantes durante a execução no arquivo de log.

---

## Logs e Depuração

Os logs são armazenados no arquivo `logs\script_log.txt` e incluem:

- Hora de início e término do script.
- Detalhes de erros e exceções.
- Eventos importantes, como atualizações de estoque e renovação de tokens.

---

## Notificações via Telegram

O script utiliza o bot Telegram configurado com o token:

- **Automatização**: `5495104211:AAHJIrse-oxrpomZrVnJvyteste`
- **Chat ID**: `codigoid`

---

## Contribuição

1. Faça um fork deste repositório.
2. Crie um branch para sua feature ou correção: `git checkout -b minha-feature`.
3. Envie suas modificações: `git commit -m 'Adicionei uma nova feature'`.
4. Envie para o branch principal: `git push origin minha-feature`.
5. Abra um pull request.