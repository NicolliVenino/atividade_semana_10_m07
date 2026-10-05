Atividade-Ponderada-M7-2026-EC
Repositório para a criação da atividade ponderada de EC 2026 - M7.

Atividade ponderada: modelo de predição com Docker
Duração total: 100 minutos

Desafio
Construa e documente uma solução conteinerizada que treine um modelo para estimar o valor futuro de uma moeda, como o Bitcoin, a partir de dados históricos. O treinamento deve ser executado em um container Docker ou em um notebook. Ao final, o modelo treinado deve ser disponibilizado em um segundo container, que executará um backend para carregá-lo e oferecer predições à aplicação.

O backend deve ser implementado obrigatoriamente em Python. A escolha das bibliotecas e da abordagem de modelagem é livre. O objetivo não é produzir uma previsão financeira confiável para uso real, mas demonstrar a integração entre treinamento, artefato do modelo, container de inferência e aplicação.

O que fazer
Desenhar a arquitetura: faça um esboço UML que represente os componentes da solução e a troca de dados entre eles. Inclua, no mínimo, o ambiente de treinamento, o artefato gerado pelo modelo, o container de inferência/backend e a aplicação cliente. Indique como o modelo treinado chega ao container de inferência.
Treinar e exportar o modelo: execute o treinamento em um container Docker ou notebook e salve o modelo em um formato que possa ser carregado posteriormente.
Preparar a inferência: implemente em Python o backend do container de inferência. Ele deve carregar o artefato treinado e disponibilizar uma operação para solicitar uma predição. Inclua também uma forma simples de verificar se o serviço está ativo.
Integrar e testar: execute os componentes necessários e demonstre que uma solicitação chega ao backend e retorna uma predição. Registre os comandos usados e os resultados observados.
Manter o devlog: documente, ao longo do desenvolvimento, as decisões, etapas realizadas, dificuldades, alterações e testes. Inclua o diagrama UML e evidências suficientes para outra pessoa compreender e reproduzir a solução.
Organização sugerida do tempo
0–15 min: compreender o desafio, escolher a abordagem e desenhar o esboço UML.
15–55 min: preparar os dados, treinar o modelo e exportar o artefato.
55–85 min: implementar e executar o backend de inferência em Python/Docker; testar a comunicação.
85–100 min: concluir o devlog e apresentar a solução e as evidências.
A distribuição é uma referência; reserve tempo para registrar o devlog durante todo o processo, não apenas no final.

Entregáveis
Esboço UML da arquitetura e do fluxo do modelo entre os componentes.
Código do treinamento e do backend em Python.
Arquivos necessários para executar os containers, como Dockerfile e configuração de serviços, quando aplicável.
Artefato do modelo treinado, ou instruções claras para gerá-lo novamente.
Devlog com decisões, comandos, testes, dificuldades e evidências da execução.
Demonstração de uma predição obtida pelo backend.
Atenção: Toda entrega deve acontecer no Github (o link de um repostório seu para isso).

Avaliação
40% — Solução funcionando: treinamento executado, artefato do modelo gerado e carregado no container de inferência, backend Python acessível e predição demonstrada.
40% — Devlog: clareza e sequência dos registros, justificativa das decisões, descrição dos testes e dificuldades, evidências e instruções que permitam compreender e reproduzir o trabalho.
20% — Observações do professor: acompanhamento do processo, participação, autonomia, colaboração e capacidade de explicar as escolhas e resolver problemas durante o desenvolvimento.
Critérios para a demonstração
Na apresentação final, mostre o diagrama UML, explique como o artefato do modelo é transferido ou disponibilizado ao container de inferência e faça ao menos uma solicitação ao backend. Informe também limitações conhecidas da solução. As predições produzidas são experimentais e não devem ser interpretadas como recomendação de investimento.

Sugestão de Fontes de Dados
Yahoo Finance: histórico de preços de BTC-USD, com opção de baixar dados diários em CSV. Em Python, pode ser acessado pela biblioteca yfinance; depende de conexão com a internet.
CryptoDataDownload: arquivos CSV históricos de diferentes criptomoedas e exchanges. É uma opção prática para evitar configurar uma API durante a atividade.
Kaggle Datasets: reúne conjuntos de dados históricos de Bitcoin e outras moedas. A qualidade varia; confira a origem, o período, a frequência e as colunas antes de usar.
Binance Spot API: permite consultar candles de mercado, com preços de abertura, máxima, mínima e fechamento, além de volume. É útil para praticar coleta por API, mas requer mais configuração.
CoinGecko API: oferece preços e outras métricas de mercado. Verifique os limites e requisitos de acesso do plano disponível antes de definir essa fonte para a atividade.
Google Dataset Search: buscador para encontrar conjuntos de dados publicados em diferentes repositórios.
Recomendação: para manter o foco nos containers, no modelo e no backend dentro dos 100 minutos, prefira fornecer ou indicar um CSV pronto com data, preço de fechamento e, se desejado, volume. Defina previamente a moeda, o período e a frequência dos dados. Para a previsão, especifique também o horizonte, por exemplo, estimar o preço de fechamento do dia seguinte. Como se trata de uma série temporal, os dados de treino e teste devem ser separados cronologicamente, sem embaralhar as linhas. A precisão do modelo não vai ser um critério punitivo, mas pode ser um diferencial levado em consideração.

Backend obrigatoriamente em python