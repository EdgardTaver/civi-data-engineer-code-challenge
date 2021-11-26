# Ideias

## Links

Necessário lidar com coordenadas geográficas.

- Esse [link](https://naysan.ca/2020/09/28/from-pandas-to-postgis-with-psycopg2/) ensina como converter longitude e latitude, se descritos em séries diferentes de um dataframe.

- Este [link](https://blog.crunchydata.com/blog/postgis-and-the-geography-type) explica como funciona o `Geography` do PostGIS.

- Acredito que deve existir alguma extensão do Pandas que permite trabalhar com o `Geography` do PostGIS.

## Perguntas

### How many users are not in any region?

O JSON que descreve os users possui coordenadas descritas de forma separada. [Com base nesse artigo](https://naysan.ca/2020/09/28/from-pandas-to-postgis-with-psycopg2/), posso carregar o JSON num DataFrame e converter para o tipo `Geography`, que de acordo com [este link](https://blog.crunchydata.com/blog/postgis-and-the-geography-type) permite fazer consultas geográficas muito mais facilmente. Imagino que já deve existir uma forma pronta de verificar se um dado ponto está dentro de uma região descrita na tabela `regions`.
> Tem mesmo como verificar se um ponto está dentro de uma região. Basta usar a função `ST_Contains` do PostGIS.

Além disso:

- Verificar o que fazer com os valores nulos. Faria sentido removê-los durante o _transform_?
- Existem users com latitude null e longigute I null, e vice-versa? O que fazer nestes casos?
- Será que faz sentido criar no `dwh` uma tabela que associa cada user a uma `region`? A resposta para a pergunta seria uma query nesta tabela.

### How many markers does each region have?

Imagino que dê pra resolver de forma muito similar ao caso dos `users`.

Além disso:

- Verificar se há **valores faltando** em algum dos `markers`.
- Criar também uma tabela no `dwh` onde cada `marker` é associado a uma `region`?

### What are the top N regions with the most users?

Com a `dwh` associando cada user a uma região, isso deve ser tranquilo de fazer com uma query simples de contagem.

Seria possível, até mesmo, pensar em construir uma tabela que já traga esse resultado.


### Geral

- Como garantir idempotência dos markers na hora de mandar os dados para a `dwh`? Aliás, faz sentido ter essa idempotência, ou é esperado vários markers exatamente nas mesmas coordenadas?

> A seguinte query retorna alguns casos de markers duplicados:
> 
> ```sql
> select point, count(*) from public.markers m
> group by point
> order by 2 desc
> ```
> 
> O que fazer com eles?

- Muito provavelmente usarei Python para o ETL. Lembrar de garantir atomicidade com lógica de commit/rollback na transação do banco.
- Será que daria para ter uns checks antes e depois de inserir dados no banco? Por exemplo: espero inserir 1000 markers na `dwh`. Após inserção, tenho mesmo os 1000 markers esperados?