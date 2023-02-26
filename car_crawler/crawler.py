from dataclasses import dataclass
import requests as rq
from bs4 import BeautifulSoup
import pendulum

@dataclass
class Carro:
  host: str
  data_consulta: str
  codigo: str
  url: str
  nome: str
  valor: str
  combustivel: str
  cor: str
  placa: str
  km: str
  ano_fabric: str
  ano_modelo: str


def get_lista_carros(host):
    lista_link_carros = []
    page = 1

    while True:

        response = rq.get(f'{host}/busca//pag/{page}/ordem/ano-desc/')

        if 'Nenhum resultado encontrado' in response.text:
                break

        soup = BeautifulSoup(response.text, 'html.parser')
        #links = soup.find_all('a', class_="btn-flat btn waves-effect ver-detalhes")
        links = soup.find_all('a')

        for l in list(links):
        #    lista_link_carros.append(l['href'])
            try:
                if '/carros' in str(l['href']):
                    lista_link_carros.append(l['href'])
            except:
                pass

        page += 1

    return list(set(lista_link_carros))

def get_detalhe_carros(host, lista_link_carros, log=False):

    lista_carros = []

    for k, link in enumerate(lista_link_carros):
        response = rq.get(f'{host}/{link}')
        
        if log:
            print(f'Buscando {host}/{link}')

        soup = BeautifulSoup(response.text, 'html.parser')

        tag_nome = soup.find('h1', class_ ="titulo-veiculo")# padding-top-20 no-margin")

        nome = ''
        try:
            nome = tag_nome.getText().split('					')[1]
        except:
            nome = tag_nome.getText()
        #print(nome)

        ###
        tag_valor = soup.find('span', id="valor_veic")
        valor = tag_valor.getText()
        #print(valor)

        ###
        tags_caracteristicas = soup.find_all('span', class_ ="secondary-content")

        if len(tags_caracteristicas) == 0:
            tags_caracteristicas = soup.find_all('span', class_ ="lead text-muted")

        if len(tags_caracteristicas) == 0:
           tags_caracteristicas = soup.find_all('strong', class_ ="ligth")

        #for kc, carac in enumerate(list(tags_caracteristicas)):
        #    print(carac.getText())
        
        #print('-------------')
        lista_caracteristicas = list(tags_caracteristicas)
        
        carro = Carro(
            host=host,
            data_consulta=pendulum.now().format('YYYY-MM-DD HH:mm:ss'),
            url=f'{host}/{link}',
            codigo=link.split('.')[-2].split('-')[-1],
            nome=nome,
            valor=valor,
            combustivel=lista_caracteristicas[0].getText().strip(),
            cor=lista_caracteristicas[1].getText().strip(),
            placa=lista_caracteristicas[2].getText().strip(),
            km=lista_caracteristicas[3].getText().strip(),
            ano_fabric=lista_caracteristicas[4].getText().strip(),
            ano_modelo=lista_caracteristicas[5].getText().strip()
            )

        lista_carros.append(carro)

    return lista_carros


import pandas as pd
from sqlalchemy import create_engine

hosts = ['https://dakarveiculos.com.br','https://uninovaveiculos.com.br','https://leocaretaveiculos.com.br']
#'https://vitoriaseminovos.com'

for host in hosts:
    
    print(f'Buscando lista carros {host}')
    lista_links = get_lista_carros(host)
    print(f'Localizados {len(lista_links)} carros')

    print(f'Buscando detalhes...')
    lista_carros = get_detalhe_carros(host, lista_links)
    
    print(f'Salvando')
    df = pd.DataFrame(lista_carros)
    engine = create_engine('postgresql://root:root@localhost:5432/local')
    df.to_sql('carro', engine, if_exists='append', index=False)

    print(f'Encerrando {host}')
    print('============================')




#Exceção ARIVES
host = 'https://arives.com.br'

response = rq.get(f'{host}/multipla/ajaxlistPaged/page/200')

soup = BeautifulSoup(response.text, 'html.parser')
print(f'Buscando lista carros {host}')
lista_link_carros = soup.find_all('a', class_='grey-text text-darken-4 swell34 class-avant')

links = []
for link in lista_link_carros:
    links.append(link['href'])
print(f'Localizados {len(links)} carros')    

lista_carros = []

print(f'Buscando detalhes...')
lista_carros = get_detalhe_carros(host, links, log=True)

print(f'Salvando')
df = pd.DataFrame(lista_carros)
engine = create_engine('postgresql://root:root@localhost:5432/local')
df.to_sql('carro', engine, if_exists='append', index=False)
print(f'Encerrando {host}')
print('============================')
