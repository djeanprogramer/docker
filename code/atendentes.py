import json
import funcoes

def getAtendentes():
	jsAtendentes = {
					 "Juliana": {
						"email": "juliana@tcheturbo.com.br",
						"senha": "juliana@2021",
						"token": "39e183e8b9415fc746563700b7de7ddf",
						"atenddance_id": "624aeef178dfb873cf7f448f"
					  },
					 "Ana": {
						"email": "anacarolina@tcheturbo.com.br",
						"senha": "anatche2021",
						"token": "39e183e8b9415fc746563700b7de7ddf",
						"atenddance_id": "624aeef178dfb873cf7f448f"
					  },
					 "Fabiana": {
						"email": "vfabiana@tcheturbo.com.br",
						"senha": "fa12ma",
						"token": "39e183e8b9415fc746563700b7de7ddf",
						"atenddance_id": "624aeef178dfb873cf7f448f"
					  },
					 "Silvana": {
						"email": "lsilvana@tcheturbo.com.br",
						"senha": "1453tche",
						"token": "39e183e8b9415fc746563700b7de7ddf",
						"atenddance_id": "624aeef178dfb873cf7f448f"
					  },
					 "Gabrielly": {
						"email": "cgabrielly@tcheturbo.com.br",
						"senha": "g01030507",
						"token": "39e183e8b9415fc746563700b7de7ddf",
						"atenddance_id": "624aeef178dfb873cf7f448f"
					  },
					 "Thais": {
						"email": "rthais@tcheturbo.com.br",
						"senha": "15051994",
						"token": "39e183e8b9415fc746563700b7de7ddf",
						"atenddance_id": "624aeef178dfb873cf7f448f"
					  }
				}

	dicio_tokens = {"Juliana": "", "Ana": "", "Fabiana": "", "Silvana": "", "Gabrielly": "", "Thais": "" }

	dicio = dict(jsAtendentes)

	aux = dicio.get('Juliana')
	parametros = {'email': {aux['email']}, 'password': {aux['senha']}}
	authJuliana = funcoes.fAutenticar(parametros)
	jauthJuliana = authJuliana.json()
	if authJuliana.status_code == 200:
		print('Autenticou Juliana')
		dicio_tokens.update({'Juliana': jauthJuliana['token']})
	else:
		print(f"Código de Status: {authJuliana.status_code} - Usuário: Juliana")
		dicio.pop("Juliana")
		dicio_tokens.pop("Juliana")

	aux = dicio.get('Ana')
	parametros = {'email': {aux['email']}, 'password': {aux['senha']}}
	auth = funcoes.fAutenticar(parametros)
	jauth = auth.json()
	if auth.status_code == 200:
		print('Autenticou Ana')
		dicio_tokens.update({'Ana': jauth['token']})
	else:
		print(f"Código de Status: {auth.status_code} - Usuário: Ana")
		dicio.pop("Ana")
		dicio_tokens.pop("Ana")

	aux = dicio.get('Fabiana')
	parametros = {'email': {aux['email']}, 'password': {aux['senha']}}
	auth = funcoes.fAutenticar(parametros)
	jauth = auth.json()
	if auth.status_code == 200:
		print('Autenticou Fabiana')
		dicio_tokens.update({'Fabiana': jauth['token']})
	else:
		print(f"Código de Status: {auth.status_code} - Usuário: Fabiana")
		dicio.pop("Fabiana")
		dicio_tokens.pop("Fabiana")

	aux = dicio.get('Silvana')
	parametros = {'email': {aux['email']}, 'password': {aux['senha']}}
	auth = funcoes.fAutenticar(parametros)
	jauth = auth.json()
	if auth.status_code == 200:
		print('Autenticou Silvana')
		dicio_tokens.update({'Silvana': jauth['token']})
	else:
		print(f"Código de Status: {auth.status_code} - Usuário: Silvana")
		dicio.pop("Silvana")
		dicio_tokens.pop("Silvana")

	aux = dicio.get('Gabrielly')
	parametros = {'email': {aux['email']}, 'password': {aux['senha']}}
	auth = funcoes.fAutenticar(parametros)
	jauth = auth.json()
	if auth.status_code == 200:
		print('Autenticou Gabrielly')
		dicio_tokens.update({'Gabrielly': jauth['token']})
	else:
		print(f"Código de Status: {auth.status_code} - Usuário: Gabrielly")
		dicio.pop("Gabrielly")
		dicio_tokens.pop("Gabrielly")

	aux = dicio.get('Thais')
	parametros = {'email': {aux['email']}, 'password': {aux['senha']}}
	auth = funcoes.fAutenticar(parametros)
	jauth = auth.json()
	if auth.status_code == 200:
		print('Autenticou Thais')
		dicio_tokens.update({'Thais': jauth['token']})
	else:
		print(f"Código de Status: {auth.status_code} - Usuário: Thais")
		dicio.pop("Thais")
		dicio_tokens.pop("Thais")

	return dicio, dicio_tokens

#di, dit = getAtendentes()

#for vAuxToken in dit:
#	funcoes.fValidacaoLogoutToken(dit[vAuxToken])

#di.items().

#print(di[1][1])

#print(di)
#print(dit)

#print(len(di))
#print(len(dit))

#print(dicio["Juliana"])

#print(dicio.get('Thais'))

#dicio = dict(jsAtendentes)
#print(dicio)

#for chave in dicio.keys():
#  print(f'Chave = {chave} e Valor = {dicio[chave]}')