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

def getAtivacoesDoDiaMovel():
  # 7 - Contratos Telefonia Móvel 
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
                  c.contract_type_id,
                  ai.final_checklist
                from contracts c
                  inner join people p 
                    on p.id  = c.client_id
                  inner join contract_events ce  
                    on ce.contract_id  = c.id 
                  inner join contract_event_types cet 
                    on cet.id = ce.contract_event_type_id    
                  inner join contract_types ct 
                    on ct.id = c.contract_type_id 
                  inner join contract_assignment_activations caa 
                    on caa.contract_id = c.id  
                  inner join assignments a 
                    on a.id = caa.assignment_id 
                  inner join assignment_incidents ai 
                    on ai.assignment_id = a.id 
                where c.id > 0
                  and cet.id = 3
                  and ce.date >= current_date  
                  and c.v_stage = 'Aprovado'
              and c.v_status = 'Normal'
              and ct.id in (7)                
              and ai.final_checklist_complete 
              and ai.incident_type_id = 1334 --ATIVACAO MOVEL
            order by 1   """
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

def getFilaAvisoBloqueioMovel(data_inicial, data_final: date):
  sql = f""" select p.id as client_id,	
                    frt.contract_id ,       
                    p.name,
                    p.phone, 
                    p.cell_phone_1,
                    p.type_tx_id,
                    frt.id as frt_id,
                    frt.expiration_date
            from financial_receivable_titles frt 
              inner join people p 
                on p.id  = frt.client_id
              inner join contracts c 
                on c.id  = frt.contract_id                     
              inner join financial_operations fo 
                on fo.id = frt.financial_operation_id  
            where frt.balance > 0   
              and not frt.deleted
              and ((frt.expiration_date >= '{data_inicial}') and (frt.expiration_date <= '{data_final}')) 
              and frt.bill_title_id is null
              and not frt.renegotiated 
              and c.v_status = 'Normal'
              and frt.financial_operation_id = 63 
            order by 5 """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getFilaAvisoBloqueioMovel() ' + str(e))
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

def getDadosPPOE(ppoe: str):
  sql = f""" select 
            c.id as contrato,
            p."name" as cliente,
            to_char(c.beginning_date,'DD/MM/YYYY') as inicio,
            p.city as cidade,
            p.state as uf,
            c.v_status as status,
            aap.title as olt,
            aap.code  as olt_codigo,
            aap."type" as tipo_olt,
            aap.ip as olt_ip,
            aap."user" as olt_user,
            aap."password" as olt_pass,
            aap.port_telnet as olt_port_telnet,
            aap.port_ftp as olt_port_ftp,
            cast(aap.coverage_degrees as varchar(50)) as olt_coverage_degrees,
            cast(aap.direction_degrees as varchar(50)) as olt_direction_degrees,
            cast(aap.degrees as varchar(50)) as olt_degress,
            aap.internet_bandwidth as olt_internet_bandwidth,
            aap.mac as olt_mac,
            aap.mac_password as olt_mac_password,
            aap.radius_port as olt_radius_port,
            aap.olt_protocol ,
            aap.secret as olt_secret,
            ct.title as tipo_contrato,
            c.automatic_blocking as bloqueio_automatico,
            ci.is_combination,
            ci.combination_contract_item_id,
            ci.description as servico,
            ac.title as concentrador,
            m.title as tipo_equipamento,
            as2.title as autenticacao,
            aig.title as grupo_ip,
            ai.ip ,
            ai.netmask,
            auc."user" as ppoe,
            auc."password" as ppoe_senha,
            auc.mac as ppoe_mac,
            auc.equipment_user as ppoe_user_equipament,
            auc.equipment_port as ppoe_equipment_port,
            auc.equipment_serial_number as ppoe_equipment_serial_number,
            auc."password" as ppoe_user_pass,
            auc.wireless_mac as ppoe_wireless_mac,
            auc.wifi_name as ppoe_wifi_name,
            auc.wifi_password as ppoe_wifi_pass,
            auc.fiber_mac as ppoe_fiber_mac,
            auc.port_olt as ppoe_port_olt,
            auc.slot_olt as ppoe_slot_olt,
            aal.title as ppoe_authenticate_adress_list,
            auc.equipment_type as ppoe_equipment_type,
            auc.provision_status as ppoe_provision_status,
            auc.additional_info as ppoe_additional_info,
            auc.vlan as ppoe_vlan
          from contracts c 
            inner join people p 
              on p.id = c.client_id
            inner join authentication_access_points aap 
              on c.authentication_access_point_id = aap.id 
            left join authentication_concentrators ac 
              on (ac.id = aap.authentication_concentrator_id and ac.active )
            left join manufacturers m 
              on m.id = aap.manufacturer_id 
            left join authentication_sites as2 
              on (as2.id = aap.authentication_site_id and not as2.deleted )
            left join authentication_ips ai 
              on (ai.id = aap.authentication_ip_id and not ai.deleted )
            left join authentication_ip_groups aig 
              on (aig.id = ai.authentication_ip_group_id and not aig.deleted)
            inner join contract_types ct 
              on ct.id = c.contract_type_id 
            inner join contract_items ci 
              on (ci.contract_id = c.id 
                  and not ci.deleted)
            inner join authentication_contracts auc
              on (auc.contract_id = c.id and auc.contract_item_id = ci.id and auc.active)
            left join authentication_address_lists aal 
              on aal.id = auc.authentication_address_list_id 
          where auc."user" = '{ppoe}'
          order by p."name"   
        """
  try:
    if ppoe != '':
      b = bd_conecta.conecta_db_tche()
      cursor = b.cursor()
      cursor.execute(sql)
      rs = cursor.fetchall()
      cursor.close()
      b.close()
      return rs
    else:
      return None
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getDadosPPOE() ' + str(e))
    return 

def getSMS_Zenvia():
  sql = f""" select 
	'55' ||
	replace(
		replace(
			(replace(aux.cell_phone_1, '(','')), 
				')','') ,
				'-','')	celular,
    to_char(frt3.expiration_date, 'DD/MM/YYYY') as vencimento,
	'R$ ' || replace(cast(frt3.title_amount as varchar(100)), '.', ',') as valor,
	frt3.typeful_line as linha_digitavel
from 
	(select p.id ,	
		 frt.contract_id,
	     p.name,
         p.phone, 
         p.cell_phone_1,      
   	     count(frt.expiration_date) as qtd_parcelas ,
		 count(frt2.client_paid_date) as qtd_pagamentos,
 		 sum(
 		 	case extract(DOW from frt.expiration_date)
			 	when 0 then (frt.expiration_date + INTERVAL '1 DAY'):: DATE - frt2.client_paid_date
			 	when 6 then (frt.expiration_date + INTERVAL '2 DAY'):: DATE - frt2.client_paid_date
			 	else frt.expiration_date - frt2.client_paid_date
 		 	end
 		 	) as dias_atraso
from financial_receivable_titles frt 
  inner join people p 
    on p.id  = frt.client_id
  inner join financial_collection_types fct 
    on fct.id = frt.financial_collection_type_id
  inner join financial_collection_type_layouts fctl 
    on fctl.id = fct.financial_collection_type_layout_id 
  inner join contracts c 
    on c.id  = frt.contract_id   
  left join financial_receipt_titles frt2 
    on frt2.financial_receivable_title_id  = frt.id 
where not frt.deleted  
  and (year (frt.expiration_date) = '2022'
        and month (frt.expiration_date) >= '05'
        and month (frt.expiration_date) < '08')
  and frt.bill_title_id is null
  and not frt.renegotiated
  and frt.balance <= 1000  
  and frt.balance <> 250    
  and not (fctl.title like '%Debito%')
 -- and p.id in ( 12938 )--12938 --15198 --15267, 15198, 
group by 1,2,3,4,5
order by frt.contract_id) as aux   
  inner join financial_receivable_titles frt3 
    on frt3.contract_id  = aux.contract_id
where frt3.expiration_date between '2022-08-01' and '2022-08-31'
  and not frt3.renegotiated
  and frt3.balance <= 1000  
  and frt3.balance <> 250    
  and frt3.balance > 0
  and frt3.bill_title_id is null
  and (aux.qtd_parcelas - aux.qtd_pagamentos > 0
 		or aux.dias_atraso <= -5 )
  and coalesce(frt3.barcode,'') <> ''
  and ('55' ||
	replace(
		replace(
			(replace(aux.cell_phone_1, '(','')), 
				')','') ,
				'-',''))	not in (  '5555999333843', '5555984434689', '5555997011505', '5555999710387', '5555996251749', '5555996370988', '5555997176889',
  '5551995360576', '5555999222759', '555597356144',  '5555999137663', '5551995403372', '5555996984201', '5555999262681', 
  '5555997119927', '5555999098815', '5555992029332', '5555999299433', '5555996704559', '5555999147577', '5555996310123', 
  '5555999878243', '5555981291883', '5555999299433', '5555997280460', '5555999299433', '5555999045359', '5555996820032', 
  '5555999037393', '5555999938540', '5555996665523', '5555997282935', '5555999988256', '5555996144983', '5555996953455', 
  '5549991686300', '5555997120283', '5555996698276', '5555996004940', '5549991686300', '5555999652370', '5555996826922', 
  '5555997047417', '5551997150096', '5555996826922', '5555996813766', '5555999052952', '5555984340137', '5555999746286', 
  '5555999473162', '5555999247051', '5554991263100', '5555996820032', '5555996488139', '5555996910120', '5555996571202', 
  '5555 996196743','5555996157902', '5555981199055', '5555996807215', '5555999247051', '5555999590350', '5555999411988', 
  '5555996617953', '5555999789430', '5555997068990', '5555999187123', '5555996109838', '5555996984997', '5555999772909', 
  '5555997331977', '5555999925406', '5555996138341', '5555999279404', '5555999957078', '5555996637867', '5555997096800', 
  '5555991441880', '5555999519768', '5555999519768', '5555999391071', '5555997068990', '5555996108952', '5555996494916', 
  '5555996727060', '5555996359467', '5555997173207', '5555999991749', '5555996122387', '5555996359467', '5555996992168', 
  '5555997165531', '5554991449571', '5555999721899', '5555996570206', '5555996832782', '5551998979864', '5555996832782', 
  '5555984238964', '5555996096675', '5555997188135', '5555999426514', '5555999270018', '5555996652877', '5538999297400', 
  '5555996106357', '5555996652877', '5555996106357', '5555999524045', '5555984375366', '5549988071330', '5555997349776', 
  '5555984375366', '5555999961654', '5555999902856', '5555996425178', '5555996359216', '5549988071330', '5555996425178', 
  '5555999288222', '5549988071330', '5555999423533', '5555997035990', '5555997329055', '5555996203242', '5555996806115', 
  '5555996629112', '5555936184455', '5555936192806', '5555996655733', '5555999236936', '5555996242652', '5555996524699', 
  '5555996783094', '5555999206466', '5555999989419', '5555999125347', '5549998368496', '5555984043748', '5555996960454', 
  '5555996256314', '5549999919205', '5555996883187', '5555984281228', '5555997283731', '5555999261134', '5555999276920', 
  '5555999236936', '5555999734421', '5555996055183', '5555996242807', '5555996000034', '5554999114723', '5555992377033', 
  '5555999478140', '5555999338264', '5555999156859', '5555999558461', '5555996951001', '5555997015207', '5555999682307', 
  '5555996153594', '5555996136519', '5555997016133', '5555997249356', '5555999594366', '5555991922039', '5555996909814', 
  '5555996986616', '5555996909814', '5555999678463', '5555999558461', '5555996100656', '5555997338707', '5555996595332', 
  '5555999823888', '5555999330489', '5555981170683', '5555999624751', '5555981170683', '5555996673918', '5555996557570', 
  '5555996866701', '5555996249342', '5555984599093', '5555996214500', '5555999339733', '5555999430203', '5555997270053', 
  '5555996131900', '5555999443661', '5554996698695', '5555981420091', '5555999042613', '5555999944432', '5555996800583', 
  '5555997354279', '5555997086098', '5555999421879', '5555999421879', '5555997254349', '5555996069283', '5555997044158', 
  '5555996336824', '5555996045054', '5555996037366', '5555999994490', '5555999621291', '5555999568582', '5555999551352', 
  '5555996656650', '5555996199993', '5547997886165', '5555999104950', '5555997167402', '5555999264373', '5555996563494', 
  '5555999826142', '5555996375001', '5555999551352', '5555996427554', '5547992158070', '5555996427554', '5555996027840', 
  '5555997286890', '5555999025225', '5555997286890', '5555997064695', '5555996312678', '5555996320159', '5555996525349', 
  '5555997125605', '5555996484378', '5555997064695', '5555996370581', '5555999547830', '5555984458850', '5555997337754', 
  '5555997125605', '5555996124767', '5555999904106', '555596398453',  '5555984461794', '5555996639895', '5555997095717', 
  '5555999210029', '5555999415380', '5555999641534', '5555996090880', '5555999922272', '5555996077355', '555599418367', 
  '5555996703969', '5555999589701', '5555999890598', '5555996298122', '5555997139543', '5555999201704', '5555999418367', 
  '555499863086',  '5555999926635', '5555996890084', '5555996890084', '5555996738697', '5555999177469', '5555996639845', 
  '5549999366792', '5555996084217', '5555996216026', '5555996216026', '5555996016444', '5555996429340', '5555999871322', 
  '5555996045202', '5555999871322', '5555999329354', '5555999838359', '5555999827172', '5555996564523', '5555997177662', 
  '5555999996020', '5555996519734', '5555999186443', '5555996970822', '5555996892184', '5555999915520', '5555999120427', 
  '5555996523780', '5555999498528', '5555996518306', '5555996939957', '5555999147031', '5555996063738', '5555999268808', 
  '5555999147942', '5555997212126', '5555996754684', '5555996553367', '5555999962560', '5551998817329', '5555999536688', 
  '5555996198063', '5555996553367', '5555996240541', '5555996390234', '5555996004707', '5555996799220', '5555996148536', 
  '5555996849231', '5555996925856', '5555999206818', '5555999886480', '5555984259222', '5555996718554', '5555997314484', 
  '5555984424074', '5555997305287', '5555999640737', '5555999197869', '5555996252146', '5551996858907', '5555996713347', 
  '5555996605149', '5555999004238', '5555996102388', '5555996060494', '5555996476944', '5555999513763', '5555996060494', 
  '5555999405865', '5555997019734', '5555996094374', '5555996387627', '5551999522588', '5555999439233', '5555996585460', 
  '5555997132895', '5555997296233', '5549988111126', '5555996025647', '5555996481567', '5555997132895', '5555999507071', 
  '5555996585460', '5549988111126', '5555996060494', '5555997248778', '5551999821012', '5555999877986', '5555996936453', 
  '5555996387627', '5555999714901', '5555999245970', '5555996743937', '5555997211097', '5555996534087', '5555997226283', 
  '5555996342708', '5555997040402', '5555999388447', '5555996569982', '5555999579779', '5555997131986', '5555999747686', 
  '5555999028828', '5555999877562', '5551982330511', '5555999567079', '5555996204187', '5555996902121', '5555999841705', 
  '5555996348169', '5555936180042', '5555999640961', '5551998735667', '5555999805765', '5555996793715', '5555996064086', 
  '5555999163199', '5555996247000', '5555996865694', '5555999989914', '5555999966622', '5555999430726', '5555996094275', 
  '5555999295660', '5553999966919', '5555984129161', '5555981668793', '5555996088697', '5548991589728', '5555996023018', 
  '5555936197707', '5547999302843', '5555996948817', '5555999188293', '5555999328533', '5555999909065', '5555999661501', 
  '5555996686196', '5555996557093', '5555996714432', '5555997092163', '5547992048376', '5555997196242', '5555999727054', 
  '5555996292972', '5555997035990', '5555999344108', '5555999141247', '5555997053855', '5555996630428', '5555999141247', 
  '5555999745300', '5555996052588', '5555997212126', '5555999662107', '5555996179633', '5555996909815', '5555996274174', 
  '5555997196242', '5555996894470', '5555997278276', '5555999156643', '5555999651293', '5555999990616', '5555996869921', 
  '5555996062500', '5555996508329', '5555996116224', '5555997263861', '5554996453793', '5555996621147', '5555999463703', 
  '5555999740169', '5555996062500', '5555999740169', '5555999782728', '5555991487775', '5555997103222', '5555999919329', 
  '5555999782728', '5555999341949', '5555999341949', '5555999876600', '5555997187029', '5555996134867', '5555996134867', 
  '5555996402601', '5555996874669', '5555981297863', '5555984224963', '5555996481809', '5555996245938', '5555981297863', 
  '5555996345515', '5555999468151', '5534998376523', '5555999126427', '5555984233063', '5555999126427', '5534998376523', 
  '5555997359005', '5555999509015', '5555999526831', '5551996624959', '5555996033015', '5555999168073', '5555996894470', 
  '5555997113471', '5555999229445', '5555999019392', '5555996748178', '5595991323134', '5555999302989', '5555996315689', 
  '5555996595332', '5555999280688', '5555996595332', '5555999280904', '5555996623655', '5555996959359', '5555996959359', 
  '5555999575174', '5555999174552', '5555996764803', '5555999839055', '5555996596141', '5555999839055', '5554999030730', 
  '5555999538436', '5555996545245', '5555996595332', '5555999908918', '5555999009897', '5555999294127', '5555996595332', 
  '5555997253791', '5555999302989', '5555996247576', '5555996084217', '5555999406811', '5555996545245', '5555999301033', 
  '5555999669321', '5555991589329', '5555997217482', '5555999889516', '5555981441860', '5555997051087', '5511973978989', 
  '5555996862599', '5555996569982', '5555991583867', '5551992499833', '5555996989203', '5555999924453', '5555991556515', 
  '5561998325669', '5555996582926', '5555996033941', '5555996647509', '5555996033941', '5555996466671', '5555996261716', 
  '5555996415548', '5555996582926', '5551999198285', '5555999836898', '5555996415548', '5555997112323', '5555997298044', 
  '5555996864823', '5555996070339', '5555996519952', '5555999348219', '5555996324471', '5555996069902', '5555999448797', 
  '5555996752263', '5555991676327', '5555999839250', '5551986398260', '5555996743339', '5555999839250', '5555999362269', 
  '5555996507948', '5555999008668', '5555996036445', '5555999812184', '5555996701413', '5555999582819', '5555999483892', 
  '5555999582819', '5555999483892', '5555996242224', '5555999712437', '5555991616023', '5555996753281', '5555991131612', 
  '5555997027163', '5555997243284', '5555997027163', '5555996005548', '5555997245576', '5555999630230', '5555996237415', 
  '5555999972640', '5555997333552', '5555997291996', '5555996948830', '5555997333552', '5555996176122', '5555984087129', 
  '5555984266726', '5555981636039', '5555999545100', '5555999950838', '5555996724803', '5555996887070', '5555999823579', 
  '5555999884255', '5555999691988', '5555999876451', '5555999884255', '5555999699445', '5555997156058', '5555 996916279', 
  '5554996135835', '555496286783',  '5555997168719', '5555997191661', '5555997191661', '5555997161140', '5555984420908', 
  '5555996397435', '5555981315225', '5555999584347', '5555999450755', '5555996350101', '5555996357606', '5555996836320', 
  '5555996756321', '5555996890768', '5555999507071', '5555996890768', '5555996489314', '5555991916291', '5555999732042', 
  '5555997005658', '5555997005658', '5555999241971', '5555996703218', '5555999775439', '5555999214283', '5555997035990', 
  '5555996456736', '5555996174741', '5555984484525', '5555996489314', '5555996335152', '5555996320164', '5555996523872', 
  '5555984576527', '5541992706322', '5551985209205', '5555997287778', '5555996359467', '5555996153674', '5555999749806', 
  '5555999104950', '5555999606614', '5555936194575', '5555999894291', '5555999367822', '5555996760746', '5511991648388', 
  '5555997143958', '5555996629959', '5555999367822', '5555997222395', '5555997294760', '5555981161499', '5555936181402', 
  '5555996314711', '5555999908934', '5555997287778', '555198393666',  '5555999132946', '5555991366426', '5551985209205', 
  '5555936189204', '5555999104950', '5555999042221', '5555999042221', '5555981420091', '5555997287778', '5555996898514', 
  '5555996432554', '5555991624531', '5555999598136', '5555996890768', '5555996795696', '5555996256621', '5555996518039', 
  '5555996764446', '5555996023577', '5554991279666', '5555999606611', '5555996023577', '5555996970514', '5555997009876', 
  '5555996376815', '5555997033315', '5555984130809', '5554991974894', '5555997275250', '5555984590315', '5555999184657', 
  '5555996217521', '5555996344875', '5555996691070', '5521980833493', '5555996658882', '5555997336822', '5555996544707', 
  '5555996302835', '5555999585651', '5555996881049', '5555999216678', '5555996497926', '5555997211699', '5555999008997', 
  '5555999349439', '5555997150910', '5555996416165', '5555999003523', '5553991026994', '5555997014100', '5555999163566', 
  '5555997218607', '5555996212854', '5555984590315', '5549989237623', '5555996840457', '5555999221561', '5555996578118', 
  '5555996207182', '5555999216196', '5555996662458', '5555999869595', '5555991925954', '5555999077502', '5555999630781', 
  '5555999408463', '5555996177005', '5555996101023', '5555999699712', '5555999187294', '5555997023272', '5555996858839', 
  '5555996008665', '5555997072792', '5555996729665', '5555999691168', '5555999685966', '5555997199379', '5555981037912', 
  '5555997035932', '5555996501911', '5555997089101', '5555997089101', '5555997198159', '5555999506302', '5555997097192', 
  '5555999582187', '5555997286383', '5555999345700', '5555996552389', '5555999654621', '555597333942',  '5555999905708', 
  '5555996973983', '5549991074166', '5551980153782', '5555999834885', '5555996396227', '5555996484563', '5555999869595', 
  '5555999648610', '5555999869595', '5555999015150', '5555999508050', '5555999668383', '5555999630781', '5555999654181', 
  '5555996385125', '5555991714758', '5555996921443', '5555997099130', '5555996921443', '5555997275717', '5555996319569', 
  '5555999310720', '5511984835181', '5555999508667', '5555999310720', '5555996536521', '5555999994242', '5555996267386', 
  '5555996267374', '5555996589239', '5555999177163', '5555996335152', '5555999177163', '5555996335152', '5555999385554', 
  '5549998147981', '5555996537940', '5555999385554', '5555999474353', '5551997676240', '5555984285964', '555597310904', 
  '5555999470607', '5555999008267', '5555996799600', '5555996934735', '5555996297743', '5555996378303', '5555999151070', 
  '5555997095155', '5555996278459', '5555997301698', '5555996267386', '5549998315210', '5555999808679', '5549998315210', 
  '5555997058333', '5555997165531', '5555999385544', '5547991070721', '5555999324978', '5549998147981', '5555996002695', 
  '5555996799600', '5555996977580', '5555996888202', '5555996896379', '5555996888202', '5555996477653', '5555984493070', 
  '5555996084745', '5555997095155', '5555999051477', '5555999038042', '5555999537789', '5555999462363', '5555999817795', 
  '5555999229807', '5555997287811', '5555996653658', '5555997217568', '5555996771052', '5555996738868', '5555996550873', 
  '5555997117837', '5555996537941', '5555996997621', '5555999756152'				)
        """
  try:
    b = bd_conecta.conecta_db_tche()
    cursor = b.cursor()
    cursor.execute(sql)
    rs = cursor.fetchall()
    cursor.close()
    b.close()
    return rs
  except Exception as e:
    logging.error('SYNSUITE_FUNCOES - getDadosPPOE() ' + str(e))
    return 
