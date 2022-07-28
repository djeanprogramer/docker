import requests
import json
from SynSuite_funcoes import getSMS_Zenvia


def fZenviaSendSMS(vToken, vFrom, vTo, vMsg: str):
    try:
        vurl_api = 'https://api.zenvia.com/v2/channels/sms/messages'

        headers = {
        'Content-Type': 'application/json',
        'X-API-TOKEN': vToken
        }

        payload = json.dumps({
        "from": vFrom,
        "to": vTo,
        "contents": [
            {
            "type": "text",
            "text": vMsg
            }
        ]
        })
        
        sms = requests.post(vurl_api, headers=headers, data=payload)
        print(sms.json())
        return sms.status_code
    except Exception as e:
        print('ZENDESK ' + str(e))
        return 0

if __name__ == "__main__":
    vTokenAPI = 'yBy1f97YFIb7P191X-ajJKRlsw9GU920GaNF'
    res = getSMS_Zenvia()
    for r in res:
        vMsgSMS = f"TCHE TURBO: Sua fatura esta disponivel para pagamento! Vcto {r['vencimento']}, {r['valor']} Linha digitavel: {r['linha_digitavel']}"
        print(r['celular'])
        print(vMsgSMS)
        fZenviaSendSMS(vTokenAPI, '', r['celular'] ,vMsgSMS)
        print('-------------------')
