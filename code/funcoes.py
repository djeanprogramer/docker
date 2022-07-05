import requests
import json
import phonenumbers

def fValidarVersao():
    try:
        versao = requests.get('https://tcheturbo.sz.chat/api/version')
        aux = versao.json()
        if versao.status_code == 200 and aux['version'] == '4':
            result = True
            print('Código de Status: ' + str(versao.status_code))
            print('Versão: ' + aux['version'])
        else:
            result = False
            print('Código de Status: ' + str(versao.status_code))
            print('Versão: ' + aux['version'])
    except:
        result = False
        print('Não foi possível validar a versão da API.')

    return result

def fValidacaoLogoutToken(vToken):
    try:
        my_headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + vToken,
        }
        logout = requests.get('https://tcheturbo.sz.chat/api/v4/auth/logout',  headers=my_headers )
        aux = logout.json()
        if logout.status_code == 200:
            print('Código de Status: ' + str(logout.status_code))
            #print('Versão: ' + aux['message'])
            result = True
        else:
            print('Código de Status: ' + str(logout.status_code))
#            print('Versão: ' + aux['message'])
#            print('Versão: ' + aux['Reason'])
            result = False
    except:
        print('Não foi possível validar a versão da API.')
        result = False

    return result

def fAutenticar(parametros):
    try:
        #parametros = {'email': 'omnichannel@tcheturbo.com.br', 'password': 'omnitche21'}
        autenticacao = requests.post('https://tcheturbo.sz.chat/api/v4/auth/login', params=parametros)
        #token = autenticacao.json()
        #print('Requisição POST realizada')
        #print(f'Código de Status: {autenticacao.status_code}')
        return autenticacao
    except:
        #print('Erro na requisição POST da autenticação.')
        #autenticacao.status_code = -1
        return False

def fEnviaWhatsapp(vCredenciais, vToken):
    try:
        my_headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + vToken,
        }

        whatsapp = requests.post('https://tcheturbo.sz.chat/api/v4/message/send', headers=my_headers, params=vCredenciais)
        #print(whatsapp.json())
        return whatsapp.status_code
    except:
        print('Crash')
        return 0

def fListarAtendentes(vToken):
    try:
        my_headers = {
            'accept': 'application/json',
            'Authorization': 'Bearer ' + vToken,
        }

        print('Listar atendentes')
        whatsapp = requests.get('https://tcheturbo.sz.chat/api/v4/campaigns', headers=my_headers)
        #print(whatsapp.json())
        return whatsapp
    except:
        print('Crash')
        return 0

def fNumeroCelularValido(pCelular: str):
    if int(pCelular[4]) >= 6 and int(pCelular[2]) <= 9:
        return pCelular
    else:
        return ''

def fgetCelular(pCelular, pTelefone: str):
    try:
        vPhone = phonenumbers.parse(str(pTelefone), 'BR')
    except:
        vPhone = ''

    try:
        vCell_Phone = phonenumbers.parse(str(pCelular), 'BR')
    except:
        vCell_Phone = ''

    if vPhone != '':
        vPhone = phonenumbers.format_number(vPhone,
                                            phonenumbers.PhoneNumberFormat.E164)
        vPhone = vPhone.replace('+', '')
        vPhone = fNumeroCelularValido(vPhone)

    if vCell_Phone != '':
        vCell_Phone = phonenumbers.format_number(vCell_Phone,
                                                    phonenumbers.PhoneNumberFormat.E164)
        vCell_Phone = vCell_Phone.replace('+', '')
        vCell_Phone = fNumeroCelularValido(vCell_Phone)

    if vPhone != '':
        return  vPhone
    elif vCell_Phone != '':
        return vCell_Phone
    else:
        return ''  
    
def fMensagemMesAnterior(NumContrato: str, Vencimento: str, TipoPessoa: str, NomePessoa: str):
    if TipoPessoa != '2':
        vNome = ''
    else:
        vNome = NomePessoa.split()
        vNome = ' ' + vNome[0]

    if NumContrato != 'None':
        vNumContrato = 'fatura referente ao contrato ' + str(NumContrato)
    else:
        vNumContrato = 'fatura'

    vMensagem = f"""Olá{vNome}, 😃

    Eu sou a *TINA - assistente virtual da Tchê Turbo*, espero que esteja tudo bem 🙂
    
    Notei que sua {vNumContrato} com vencimento na data de {Vencimento} está em aberto aqui conosco, entendo que imprevistos podem acontecer, por isso estou disponível para te auxiliar.
    
    📲Você pode acessar a *2ª via do boleto* em nossa central do assinante no site https://portal.tcheturbo.com.br/person_users/login, basta informar o número do seu CPF (sem pontuação).
    
    Se você já efetuou o pagamento, pode desconsiderar essa mensagem, viu 😉
    
    Preciso te lembrar que, caso o pagamento não seja realizado, o serviço pode ser suspenso.
    
    📲Aproveita e adiciona meu WhatsApp (55) 2010-0000, quando tiver dúvidas é só me chamar!😊
    
    Até mais! 👋
    """
    return vMensagem


