from datetime import date
import logging
from sqlite3 import SQLITE_CREATE_INDEX
#from termios import 
from SZChat_funcoes import getContratosNaoEnviar

from typepy import Integer
import bd_conecta

def getAtivacoesDoDia(vTiposContratoIn: str):
  #tipos de contratos: 3- Contrato Pessoa Física
  #                    5 - Contrato Pessoa Jurídica
  #                    7 - Contratos Telefonia Móvel 
  
  sql = f"""  select 
                  ce.date ,
                  p.id as cliente_id,	
                  c.id as contrato_id,
                  case 
                  when p.type_tx_id = '1' then
                    'PJ'
                  when p.type_tx_id = '3' then
                    'EX'
                  else
                    'PF'		
                end as vPJPF,
                rtrim(p.name) as nome,
                p.phone as telefone,  
                p.cell_phone_1 as celular,
                p.email as email,
                c.v_stage as stage,
                c.v_status as status,
                c.amount ,
                c.collection_day ,
                c.contract_type_id
              from contracts c
                inner join people p 
                  on p.id  = c.client_id
                inner join contract_events ce  
                  on ce.contract_id  = c.id 
                inner join contract_event_types cet 
                  on cet.id = ce.contract_event_type_id    
                inner join contract_types ct 
                  on ct.id = c.contract_type_id 
              where c.id > 0
                and cet.id = 3
                and ce.date >= current_date  
                and c.v_stage = 'Aprovado'
                and c.v_status = 'Normal'
                and ct.id in ({vTiposContratoIn})                
              order by 1                 
        """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    logging.debug('BD TCHE: DESCONECTOU')
    return rs
  except Exception as e:
    logging.error('2SYNSUITE_FUNCOES - getAtivacoesDoDia() ' + str(e))
    return 

def getAtivacoesDoDiaPlano(contrato: str):
  sql = f"""    select 
    ci.description 
  from contracts c
    inner join contract_items ci 
      on ci.contract_id = c.id
    inner join service_products sp
      on sp.id = ci.service_product_id 
  where c.id = {contrato}
    and not ci.deleted 
    and sp.active 
    and sp.service_type in (3,4) 
  order by 1"""
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getAtivacoesDoDiaPlano() ' + str(e))
    return 

def getPrazoMedioRecebimento():
  sql = f""" select 
                p.id as client_id ,
                c.id as contract_id ,
                p.name,
                c.beginning_date ,
                frt.spc,
                frt.issue_date as vData_Emissao,
                frt.expiration_date ,
                pgto.receipt_date as vData_Pagamento,
                frt.title_amount as vValor,
                frt.balance as vSaldo,
                timestampdiff(day, frt.expiration_date, pgto.receipt_date) as vDias,
              (select 
                  count(c2.id) 
                from contracts c2
                  inner join contract_events ce2  
                    on ce2.contract_id  = c2.id 
                  inner join contract_event_types cet2 
                    on cet2.id = ce2.contract_event_type_id    
                  inner join contract_types ct2 
                    on ct2.id = c2.contract_type_id 
                where c2.id = c.id 
                  and cet2.id  in (40)
                  and not ce2.deleted 
                  order by  1 desc
                ) as qtd_bloqueios
              from financial_receivable_titles frt 
                inner join people p 
                  on p.id  = frt.client_id
                left join financial_receipt_titles as pgto
                  on frt.id = pgto.financial_receivable_title_id  
                inner join financial_collection_types fct 
                  on fct.id = frt.financial_collection_type_id
                inner join contracts c 
                  on c.id  = frt.contract_id                     
              where not frt.deleted 
                and frt.expiration_date > str_to_date(date_format(DATE_SUB(current_date , INTERVAL 3 MONTH), '%Y-%c-01'), '%Y-%c-%d')
                and frt.expiration_date < date_format(current_date,'%Y-%c-01')
                and frt.bill_title_id is null
                and not frt.renegotiated
                and frt.balance <= 1000
                and frt.balance <> 250
              order by 2, 6  
        """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    logging.debug('BD TCHE: DESCONECTOU')
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getPrazoMedioRecebimento() ' + str(e))
    return     

def getFilaParcelaVencida(data_inicial, data_final: date):
  vDesconsiderarContratos = getContratosNaoEnviar('1')
  if vDesconsiderarContratos != '':
    vDesconsiderarContratos = f' and frt.contract_id not in ({vDesconsiderarContratos}) ' 
  else:
    vDesconsiderarContratos = ''

  sql = f"""select p.id as client_id,	
                frt.contract_id ,       
                  p.name,
                  p.phone, 
                  p.cell_phone_1,
                  p.type_tx_id,
                  frt.id as frt_id,
                  min(frt.expiration_date) as expiration_date
            from financial_receivable_titles frt 
              inner join people p 
                on p.id  = frt.client_id
              inner join financial_collection_types fct 
                on fct.id = frt.financial_collection_type_id
              inner join contracts c 
                on c.id  = frt.contract_id
              left join sale_requests sr 
                on sr.id = frt.sale_request_id    
            where frt.balance > 0 
              and not frt.deleted
              and frt.expiration_date between '{data_inicial}' and '{data_final}'
              and frt.bill_title_id is null
              and not frt.renegotiated
              and frt.balance <= 1000  
              and frt.balance <> 250       
              and (((not sr.deleted) and sr.situation = 3)
                  or ( coalesce(frt.sale_request_id,0) = 0))  
              {vDesconsiderarContratos}
            group by 1,2,3,4,5,6,7
            order by p.name, frt.contract_id """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getFilaParcelaVencida() ' + str(e))
    return 

def getFilaAvisoBloqueio(data_vencimento: date):
  sql = f""" select  
	    p.id as client_id, 	
      p.name,
      p.phone, 
      p.cell_phone_1,
      frt.expiration_date,
      frt.contract_id,
      0 as frt_id,
      p.type_tx_id,
      sum(frt.balance) as balance 
from financial_receivable_titles frt 
  inner join people p 
    on p.id  = frt.client_id
  inner join contracts c 
    on c.id  = frt.contract_id    
  left join sale_requests sr 
    on sr.id = frt.sale_request_id    
where frt.balance > 0 
  and not frt.deleted 
  and frt.expiration_date = '{data_vencimento}'
          and frt.bill_title_id is null
          and not frt.renegotiated
          and frt.balance <= 1000
          and frt.balance <> 250
          and frt.balance > 0
          and p.type_tx_id = 2
          and ((not sr.deleted and sr.situation = 3)
              or (coalesce(frt.sale_request_id,0) = 0))
  group by 1,2,3,4,5,6,7
  order by 2"""
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getFilaAvisoBloqueio() ' + str(e))
    return 

def getSituacaoParcela(vFrtID: Integer):
  sql = f"""select frt.id 
            from financial_receivable_titles frt 
            where frt.id = {vFrtID}
              and not frt.deleted
              and frt.bill_title_id is null
              and not frt.renegotiated 
              and frt.balance > 0  """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getSituacaoParcela() ' + str(e))
    return 

def getFilaSerasaSPC(data_inicial, data_final: date):
  sql = f"""select 
              p.id,	
              p.name,
              p.phone, 
              p.cell_phone_1,
              min(frt.expiration_date) as expiration_date,
              c.id as contract_id,
              0 as balance,
              p.type_tx_id,
              '' as enviado ,
              c.v_status,
              c.client_id
            from financial_receivable_titles frt 
              inner join people p 
                on p.id  = frt.client_id
              inner join contracts c 
                on c.id  = frt.contract_id  
              left join sale_requests sr 
                on sr.id = frt.sale_request_id
            where not frt.deleted
              and (frt.expiration_date between '{data_inicial}' and '{data_final}')
              and frt.bill_title_id is null
              and not frt.renegotiated
              and frt.balance <= 1000
              and frt.balance <> 250
              and frt.balance > 0
              and not frt.spc
              and (c.v_status = 'Bloqueio Administrativo' or c.v_status = 'Bloqueio Financeiro')
              and ((not sr.deleted and sr.situation = 3)
                  or ( coalesce(frt.sale_request_id,0) = 0))
            group by 1,2,3,4,6,7,8,9,10     
            order by 2, 5"""
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getFilaSerasaSPC() ' + str(e))
    print(str(e))
    return 

def getFilaAvisoFimImpressaoBoletos():
  # Essa função vai buscar TODOS os clientes que possuem boleto impresso pelo Sicredi
  # e a quantidade de vezes que pagaram no caixa da tcheturbo no ano corrente.
  # Definimos descartar num primeiro momento clientes que não tem entre 10 e 40 anos
 
  sql = f"""select 
	c.id as contract_id,	
	c.client_id ,
	p.name ,
  p.type_tx_id ,
	p.phone ,
	p.cell_phone_1 ,
	p.birth_date ,
	case 
		when p.birth_date <= '1922-01-01' then 	
			cast( null as integer)
		else
			cast( TO_CHAR(AGE(now(), p.birth_date), 'YY') as integer) 
	end as vIdade,	
	tp_cobranca.title as tipo_cobranca,
	(select 
			count(titulo.id)
		from financial_receivable_titles as titulo
		  inner join financial_receipt_titles as pgto
		    on titulo.id = pgto.financial_receivable_title_id  
		  inner join bank_accounts ba1 
		    on ba1.id = titulo.bank_account_id 
		  inner join bank_accounts ba_cx1
		    on ba_cx1.id = pgto.bank_account_id 
		where titulo.client_id = c.client_id 
		  and titulo.contract_id = c.id 
		  and year(pgto.receipt_date) = year(now()) 
		  and titulo.financial_collection_type_id =  4 	
		  and pgto.bank_account_id  <> 16
		  and not titulo.renegotiated
		  and not titulo.deleted  
		  and titulo.bill_title_id is null
	) as vquantidade
from contracts c 
  inner join people p 
    on p.id = c.client_id 
  inner join financial_collection_types tp_cobranca   
    on tp_cobranca.id = c.financial_collection_type_id 
where financial_collection_type_id = 4
  and c.v_status <> 'Cancelado'
  and c.id in(3311, 3366, 3386, 3396, 3427, 3432, 3509, 3521, 3525, 3526, 3530, 3551, 3565, 3577, 3661, 3686, 3708, 3714, 3750, 3809, 3827, 3830, 3858, 3885, 3890, 3893, 3896, 3923, 3964, 3965, 3991, 3998, 4002, 4016, 4020, 4042, 4054, 4059, 4067, 4114, 4120, 4145, 4154, 4160, 4165, 4171, 4188, 4205, 4207, 4209, 4211, 4213, 4227, 4228, 4247, 4249, 4250, 4256, 4271, 4288, 4297, 4298, 4329, 4333, 4341, 4352, 4355, 4376, 4403, 4411, 4448, 4454, 4458, 4464, 4468, 4482, 4486, 4504, 4559, 4575, 4587, 4594, 4598, 4603, 4611, 4625, 4646, 4657, 4681, 4697, 4762, 4776, 4780, 4788, 4790, 4855, 4885, 4887, 4892, 4921, 4938, 4971, 4989, 4994, 5026, 5030, 5042, 5043, 5046, 5053, 5054, 5062, 5073, 5079, 5084, 5146, 5211, 5221, 5249, 5250, 5277, 5278, 5280, 5294, 5296, 5307, 5313, 5319, 5326, 5328, 5329, 5337, 5352, 5356, 5370, 5404, 5412, 5417, 5484, 5498, 5505, 5512, 5513, 5555, 5560, 5579, 5617, 8926, 13895 )
order by 10 desc
  """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()

    vRetorno = []
    for r in rs:
      if int(r['vidade'] or 0) >= 10 and int(r['vidade'] or 0) <= 40:
        vRetorno.append(r)

    cursor.close()
    b.close()
    return vRetorno
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getFila_aviso_fim_impressao_boletos() ' + str(e))
    return 
