import requests
import json
import pandas as pd
import time
import os

#python -m pip install pandas
#python -m pip install openpyxl

#Doc API
#https://pedzap.docs.apiary.io/#reference/pedidos/pedidospedstatusoffset/listar-pedidos?console=1

token = ""
host = "https://www.pedzap.com.br"
header = {"Accept":"application/json", "Content-Type":"application/json", "Auth-Token":token}


#INFORMAR CSV OU EXCEL
dataFiles = "EXCEL"
excelFileName = "pedZapData.xlsx"

dataFolder = "./data"

if not os.path.exists(dataFolder):
    os.mkdir(dataFolder)

def getLastOffset(fileName):
  if dataFiles == "CSV":
    arquivo = os.path.join(dataFolder, fileName + ".csv")

  else:
    arquivo = os.path.join(dataFolder,excelFileName) 

  if not os.path.exists(arquivo):
    return 0
  
  else:
    if dataFiles == "CSV":
      df = pd.read_csv(arquivo, header=0, sep=";")
      return df[df.columns[0]].count()
      
    else:
      excelFile = pd.ExcelFile(os.path.join(dataFolder,excelFileName))
      
      if not fileName in excelFile.sheet_names:
        return 0
      else: 
        df = pd.read_excel(open(arquivo, 'rb'), sheet_name=fileName)
        return df[df.columns[0]].count()

def getIdsFromFile(fileName, keyColumn):
  if dataFiles == "CSV":
    arquivo = os.path.join(dataFolder, fileName + ".csv")
   
  else:
    arquivo = os.path.join(dataFolder,excelFileName) 


  if not os.path.exists(arquivo):
      return []  


  if dataFiles == "CSV":
    df = pd.read_csv(os.path.join(dataFolder, fileName + ".csv"), header=0, sep=";")

    return list(df[keyColumn])

  else:
    
    excelFile = pd.ExcelFile(os.path.join(dataFolder,excelFileName))
      
    if not fileName in excelFile.sheet_names:
      return 0
    else: 
      df = pd.read_excel(open(arquivo, 'rb'), sheet_name=fileName)
      return list(df[keyColumn])

def keyExists(fileName, keyColumn, value):
  if dataFiles == "CSV":
    arquivo = os.path.join(dataFolder, fileName + ".csv")
   
  else:
    arquivo = os.path.join(dataFolder,excelFileName) 


  if not os.path.exists(arquivo):
      return False 


  if dataFiles == "CSV":
    df = pd.read_csv(os.path.join(dataFolder, fileName + ".csv"), header=0, sep=";")
    newDf = df[df[keyColumn] == value]
    return newDf[keyColumn].count() > 0
    
  else:
    
    excelFile = pd.ExcelFile(os.path.join(dataFolder,excelFileName))
      
    if not fileName in excelFile.sheet_names:
      return False
    else: 
      df = pd.read_excel(open(arquivo, 'rb'), sheet_name=fileName)
      newDf = df[df[keyColumn] == value]
      return newDf[keyColumn].count() > 0

def saveToExcel(file, header, mode, sheetName, data, offset):
  #print("{} {} {} {}".format(file,header,mode,sheetName))
  startrow = 0 if header==True else offset + 1
  with pd.ExcelWriter(file, mode=mode, header=header, encoding="utf-8-sig") as writer:
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets) #because bug pandas https://github.com/pandas-dev/pandas/issues/28653 and keep other sheets
    data.to_excel(writer, header = header, sheet_name = sheetName, index = False, startrow = startrow)

def saveToCsv(file, header, mode, data):
  data.to_csv(file, index = None, encoding="utf-8-sig", sep = ";", header = header, mode = mode)

def saveToFile(fileName, data, offset, **kwargs):
  
  if dataFiles == "CSV":
    arquivo = os.path.join(dataFolder, fileName + ".csv")
    
    if 'header' in kwargs:
      header = kwargs.get('header')
    else:
      header = offset == 0
    
    if 'mode' in kwargs:
      mode = kwargs.get('mode')
    else:
      mode = "w" if offset == 0 else "a"
    
    saveToCsv(file=arquivo, header=header, mode=mode, data=data)

  elif dataFiles == "EXCEL":
    arquivo = os.path.join(dataFolder, excelFileName) 
    
    header = offset == 0
    modeExcel = 'a' if os.path.exists(arquivo) else 'w' #exceptional mode to excel file
    
    saveToExcel(file=arquivo, header=header, mode=modeExcel, sheetName=fileName, data=data, offset=offset)

#CLIENTES
print("Buscando CLIENTES")

nomeArquivoCli = "Clientes"
offsetCli = getLastOffset(nomeArquivoCli)

retorno = requests.get(host + "/apiv1/clientes/" + str(offsetCli), headers=header)

if (retorno.ok): 
    
    json_retorno = json.loads(retorno.text)
    #print(json_retorno)
    df_cli = pd.DataFrame(json_retorno)

    print("--> gravando arquivo clientes")
    saveToFile(fileName=nomeArquivoCli, data=df_cli, offset=offsetCli)

else:
  if retorno.status_code != 400:
    print("Erro ao buscar clientes - error {}".format(retorno.status_code))

print("=====================================")

#PEDIDOS

colunasIndesejadasPedido = ["ped_hash","ped_origem","ped_cep","ped_endereco","ped_numero","ped_complemento","ped_pontoreferencia","ped_tempo","ped_trocopara",
"ped_kilometragem","ped_desconto","ped_desconto_cupom","ped_observacoes","ped_agendamento","ped_breakpoint","ped_cupomfiscal_nome_razao",
"ped_cupomfiscal_cpf_cnpj","ped_mercadopago_status","ped_picpay_status","ped_pagseguro_status","ped_cielo_status","ped_datapreparo","ped_errosprocesso",
"ped_cupomfiscal","ent_id","pedidos_itens","qrcode_entregador","mes_hash"]

#dicionarioStatus = {"ABE": "aberto","AJU": "ajuda","PEN": "pendente","ACE": "aceito","PRE": "preparado",
#"LOC": "no local","ENT": "entregue","RET": "retirado","COM": "completo","AVA": "avaliado","REJ": "rejeitado",
#"REG": "região não atendida", "DES": "desistência"}

dicionarioStatus = {"ACE": "aceito"}
listaStatus = list(dicionarioStatus.keys())

nomeArquivoPed = "Pedidos"

for i in range(len(listaStatus)):

  descricaoStatus = dicionarioStatus.get(listaStatus[i])

  #"pedidos {}_{}.csv".format(descricaoStatus, time.strftime("%Y%m%d%H%M%S"))
  offsetPed = getLastOffset(nomeArquivoPed)
  
  print("Buscando PEDIDOS")
  
  retorno = requests.get(host + "/apiv1/pedidos/" + listaStatus[i] + "/" + str(offsetPed), headers=header)
  
  if (retorno.ok): 
    
    json_retorno = json.loads(retorno.text)
    #print(json_retorno)
    df_ped = pd.DataFrame(json_retorno)
    
    df_ped.drop(colunasIndesejadasPedido, axis = 1, inplace=True)
    
    print("--> gravando arquivo pedidos")
    #df_ped.to_csv(nomeArquivoPed, index = None, encoding="utf-8-sig", sep = ";", header = headerArquivoPed, mode = modoArquivoPed)
    saveToFile(fileName=nomeArquivoPed, data=df_ped, offset=offsetPed)

  else:
    if retorno.status_code != 400:
      print("Erro ao buscar pedidos {} - error {}".format(descricaoStatus,retorno.status_code))

print("=====================================")

#ITENS
nomeArquivoItens = "ItensPedidos"

colunasIndesejadasItens = ["ite_modo_preco","perguntas"]
listaIdPedidos = getIdsFromFile(nomeArquivoPed,"ped_id")

#listaIdPedidos.extend(list(df_ped.loc[df_ped["pedidos_itens"]==True]["ped_id"])) 



for i in range(len(listaIdPedidos)):
  pedId = listaIdPedidos[i]

  offsetPedItens = getLastOffset(nomeArquivoItens)
  headerArquivoItens = offsetPedItens == 0 and i == 0
  modoArquivoItens = "w" if offsetPedItens == 0 and i == 0 else "a"
  print("Verificando pedido id {}".format(pedId))

  if not keyExists(nomeArquivoItens,"ped_id",pedId):
    print("Buscando ITENS pedido id {}".format(pedId))
      
    retorno = requests.get(host + "/apiv1/pedidos_itens/" + str(pedId) , headers=header)

    if (retorno.ok): 
      
      json_retorno = json.loads(retorno.text)
      
      df_itens = pd.DataFrame(json_retorno)
      df_itens.drop(colunasIndesejadasItens, axis = 1, inplace=True)
      df_itens["ped_id"] = pedId
      #df_itens['ite_preco'] = df_itens['ite_preco'].astype(float)

      print("--> gravando arquivo itens pedidos id {}".format(pedId))

      #df_itens.to_csv(nomeArquivoItens, index = None, mode = modoArquivoItens, header = headerArquivoItens, encoding="utf-8-sig", sep = ";")
      saveToFile(fileName=nomeArquivoItens, data=df_itens, offset=offsetPedItens, mode=modoArquivoItens, header=headerArquivoItens)

    else:
      if retorno.status_code != 400:
        print("Erro ao buscar itens pedido id {} - error {}".format(pedId,retorno.status_code))

print("=====================================")

#PERGUNTAS ITENS
nomeArquivoPerguntaItens = "PerguntasItens"

colunasIndesejadasPerguntas = ["per_mediaponderada","per_grupo","respostas"]

listaIdItens = getIdsFromFile(nomeArquivoItens,"ite_id")

for i in range(len(listaIdItens)):
  itemId = listaIdItens[i]

  offsetPerguntaItens = getLastOffset(nomeArquivoPerguntaItens)
  headerArquivoPerguntaItens = offsetPerguntaItens == 0 and i == 0
  modoArquivoPerguntaItens = "w" if offsetPerguntaItens == 0 and i == 0 else "a"
  print("Verificando PERGUNTAS item id {}".format(itemId))

  if not keyExists(nomeArquivoPerguntaItens,"ite_id",itemId):
    print("Buscando perguntas item id {}".format(itemId))
      
    retorno = requests.get(host + "/apiv1/pedidos_itens_perguntas/" + str(itemId) , headers=header)

    if (retorno.ok): 
      
      json_retorno = json.loads(retorno.text)
      
      df_perguntas = pd.DataFrame(json_retorno)
      df_perguntas.drop(colunasIndesejadasPerguntas, axis = 1, inplace=True)
      df_perguntas["ite_id"] = itemId
      
      print("--> gravando arquivo perguntas item id {}".format(itemId))

      saveToFile(fileName=nomeArquivoPerguntaItens, data=df_perguntas, offset=offsetPerguntaItens, mode=modoArquivoPerguntaItens, header=headerArquivoPerguntaItens)

    else:
      if retorno.status_code != 400:
        print("Erro ao buscar perguntas item id {} - error {}".format(itemId,retorno.status_code))

print("=====================================")

#RESPOSTAS PERGUNTAS
nomeArquivoRespostasPergunta = "RespostasPerguntas"

listaIdPerguntas = getIdsFromFile(nomeArquivoPerguntaItens,"per_id")

for i in range(len(listaIdPerguntas)):
  perguntaId = listaIdPerguntas[i]

  offsetRespostasPergunta = getLastOffset(nomeArquivoRespostasPergunta)
  headerArquivoRespostasPergunta = offsetRespostasPergunta == 0 and i == 0
  modoArquivoRespostasPergunta = "w" if offsetRespostasPergunta == 0 and i == 0 else "a"
  print("Verificando RESPOSTAS pergunta id {}".format(perguntaId))

  if not keyExists(nomeArquivoRespostasPergunta,"per_id",perguntaId):
    print("Buscando respostas pergunta id {}".format(perguntaId))
      
    retorno = requests.get(host + "/apiv1/pedidos_itens_respostas/" + str(perguntaId) , headers=header)

    if (retorno.ok): 
      
      json_retorno = json.loads(retorno.text)
      
      df_respostas = pd.DataFrame(json_retorno)
      #df_respostas.drop(colunasIndesejadasPerguntas, axis = 1, inplace=True)
      df_respostas["per_id"] = perguntaId
      
      print("--> gravando arquivo respostas pergunta id {}".format(perguntaId))

      saveToFile(fileName=nomeArquivoRespostasPergunta, data=df_respostas, offset=offsetRespostasPergunta, mode=modoArquivoRespostasPergunta, header=headerArquivoRespostasPergunta)

    else:
      if retorno.status_code != 400:
        print("Erro ao buscar respostas pergunta id {} - error {}".format(perguntaId,retorno.status_code))
