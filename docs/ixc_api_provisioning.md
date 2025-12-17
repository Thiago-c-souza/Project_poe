# Guia rápido: corrigir erro "Campo de script em branco" ao provisionar ONU via API

Quando a chamada `botao_gravar_dispositivo_*` retorna HTML com a mensagem "Falha ao autorizar ONU! Campo de script em branco",
o problema costuma ser a ausência do identificador do script que deve ser aplicado na ONU.

## Resumo da causa
- O endpoint de gravação espera o ID do cliente fibra **e** o ID do script configurado para a ONU.
- Se o campo de script não é enviado (ou chega vazio), o backend responde com uma página HTML informando que o script está em branco,
  mesmo que o status HTTP seja 200.

## Como resolver
1. Identifique o ID do script utilizado na interface web (em "Scripts de ONU" ou equivalente). Muitas instalações expõem um endpoint
   `fh_scripts_onu_<empresa>` ou `listar_scripts_onu` que retorna os scripts disponíveis; utilize qualquer um deles para obter o
   identificador correto.
2. Envie esse ID junto com o `id` do cliente fibra na chamada `botao_gravar_dispositivo_*`.

### Exemplo de requisição
```python
import base64
import json
import requests

BASE = "https://sistema.liveinternet.com.br/webservice/v1"
auth_header = "Basic <token>"  # Substitua pelo token real

cliente_id = "24339"          # retornado em "Cliente fibra criado"
script_id = "35441"           # ID do script selecionado/consultado previamente
url = f"{BASE}/botao_gravar_dispositivo_22408"

headers = {
    "Authorization": auth_header,
    "Content-Type": "application/json",
}
payload = {
    "id": cliente_id,
    "script": script_id,      # chave aceita pelo endpoint; algumas instalações usam "id_script"
    "id_aci": cliente_id,     # inclui se sua coleção Postman mostrar este campo
}

response = requests.post(url, headers=headers, json=payload, timeout=30)
response.raise_for_status()

raw_body = response.text
if "Campo de script em branco" in raw_body:
    raise RuntimeError("Script não enviado: defina 'script'/'id_script' com o ID correto")

# Em respostas HTML, extraia o texto entre <div class="panel-heading-fail"> para depuração
print("Resposta:", raw_body)
```

### Dicas adicionais
- Se o `get_id` vier em Base64 (como no endpoint `fh_onu_nao_autorizadas_*`), decodifique-o para confirmar quais variáveis o backend
  espera. Um `SCRIPT` ou `id_script` vazio é um sinal de que você precisa preencher o campo antes de gravar o dispositivo.
- Sempre valide respostas HTML: elas trazem a mensagem de erro amigável que o status 200 não sinaliza.
- Mantenha o mesmo par `id`/`id_aci` que a interface web envia; divergências podem gerar erros silenciosos.
