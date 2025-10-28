import copy
import time

CUSTO_PLACA = 1000.00
CUSTO_POR_CM = 0.01
MARGEM = 10 
DIMENSAO_PLACA = 300
DIMENSAO_FINAL = DIMENSAO_PLACA - 2 * MARGEM #280 cm

# variáveis que vão guardar a melhor solução
melhorCusto = float('inf') #inf = infinito pq precisa começar com o maior valor possível pra depois minimizar
melhorAlocacao = []
melhorSequencia = []

def lerPecas(nomeArq):
    pecas = []
    with open(nomeArq, 'r') as arquivo:
        qtdePeças = int(arquivo.readline())
        for _ in range(qtdePeças):
            altura, comprimento = map(int, arquivo.readline().split())
            pecas.append((altura, comprimento))
    return pecas

def posicaoEhValidaECusto(pecasAlocadas, altura, largura, posicaoX, posicaoY):
    limiteMax = DIMENSAO_PLACA - MARGEM  

    if (posicaoX < MARGEM or 
        posicaoY < MARGEM or 
        posicaoX + largura > limiteMax or 
        posicaoY + altura > limiteMax):
        return False, 0.0

    for alocadaPosX, alocadaPosY, alocadaAltura, alocadaLargura in pecasAlocadas:
        
        # limites da nova peça
        novaX1 = posicaoX
        novaX2 = posicaoX + largura
        novaY1 = posicaoY
        novaY2 = posicaoY + altura

        # limites da peça alocada
        alocadaX1 = alocadaPosX
        alocadaX2 = alocadaPosX + alocadaLargura
        alocadaY1 = alocadaPosY
        alocadaY2 = alocadaPosY + alocadaAltura

        # sobrepõe se os intervalos x e y cruzarem 
        if novaX1 < alocadaX2 and novaX2 > alocadaX1 and novaY1 < alocadaY2 and novaY2 > alocadaY1:
            return False, 0.0

    # cálculo do custo de corte embutido
    perimetro = 2 * (altura + largura)
    custoCorte = perimetro * CUSTO_POR_CM
    return True, custoCorte

def qualPrimeiraPosicaoValida(pecasAlocadas, altura, largura):
    limiteMax = DIMENSAO_PLACA - MARGEM
    
    for y in range(MARGEM, limiteMax):
        
        # só continua se a peca couber na vertical nessa linha y
        if y + altura <= limiteMax:
            
            for x in range(MARGEM, limiteMax):
                
                # so continua se a peca couber na horizontal nessa coluna x
                if x + largura <= limiteMax:
                
                    valido, custoCorte = posicaoEhValidaECusto(pecasAlocadas, altura, largura, x, y)
                    
                    if valido:
                        return x, y, custoCorte
    
    # se os ifs não tiverem retorno, a peca nao coube
    return None, None, 0.0

def backtracking(pecasParaAlocar, pecasUsadas, placasAtuais, custoAtual, sequenciaAtual):
    global melhorCusto, melhorAlocacao, melhorSequencia

    if len(sequenciaAtual) == len(pecasParaAlocar):
        if custoAtual < melhorCusto:
            melhorCusto = custoAtual
            melhorAlocacao = copy.deepcopy(placasAtuais)
            melhorSequencia = copy.deepcopy(sequenciaAtual)
        return

    for i in range(len(pecasParaAlocar)):
        if not pecasUsadas[i]:
            
            # escolher qual peça restante vai tentar encaixar
            pecasUsadas[i] = True
            pecaAtual = pecasParaAlocar[i]
            altura, largura = pecaAtual
            
            novaSequencia = sequenciaAtual + [pecaAtual]
            
            posicaoEncontrada = False
            idPlacaAlocada = -1
            pecaAlocadaInfo = None
            custoDoCorte = 0.0

            # tenta encaixar
            for idPlaca, pecasNaPlaca in enumerate(placasAtuais):
                posX, posY, custoCorte = qualPrimeiraPosicaoValida(pecasNaPlaca, altura, largura)
                
                if posX is not None: 
                    posicaoEncontrada = True
                    idPlacaAlocada = idPlaca
                    pecaAlocadaInfo = (altura, largura, posX, posY)
                    custoDoCorte = custoCorte
                    
                    placasAtuais[idPlaca].append(pecaAlocadaInfo)
                    
                    backtracking(pecasParaAlocar, pecasUsadas, placasAtuais, custoAtual + custoDoCorte, novaSequencia)
                    
                    # retrocede
                    placasAtuais[idPlaca].pop() 
                    break 

            # se nao coube, pega nova placa
            if not posicaoEncontrada:
                valido, custoCorte = posicaoEhValidaECusto([], altura, largura, MARGEM, MARGEM)
                
                if valido: 
                    pecaAlocadaInfo = (altura, largura, MARGEM, MARGEM)
                    custoDoCorte = custoCorte
                    
                    placasAtuais.append([pecaAlocadaInfo])
                    
                    custoComNovaPlaca = custoAtual + custoDoCorte + CUSTO_PLACA
                    backtracking(pecasParaAlocar, pecasUsadas, placasAtuais, custoComNovaPlaca, novaSequencia)
                    
                    # retrocede
                    placasAtuais.pop() 

            #retrocede (permuta)
            pecasUsadas[i] = False
