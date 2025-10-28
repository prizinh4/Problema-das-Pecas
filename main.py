CUSTO_PLACA = 1000.00
CUSTO_POR_CM = 0.01
MARGEM = 10 
DIMENSAO_PLACA = 300
DIMENSAO_FINAL = DIMENSAO_PLACA - 2 * MARGEM #280 cm

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