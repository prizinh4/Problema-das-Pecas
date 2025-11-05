# João de Jesus e Avila
# Priscila Andrade de Moraes

import copy
import time
import sys
from collections import namedtuple 
from typing import List, Tuple, Optional

CUSTO_PLACA = 1000.00
CUSTO_POR_CM = 0.01
MARGEM = 10 
DIMENSAO_PLACA = 300
DIMENSAO_FINAL = DIMENSAO_PLACA - 2 * MARGEM # 280 cm

Peca = namedtuple("Peca", ["altura", "largura"]) 
PecaAlocada = namedtuple("PecaAlocada", ["x", "y", "altura", "largura"])

Placa = List[PecaAlocada]

melhorCusto: float = float('inf') # começa com infinito pra poder minimizar
melhorAlocacao: List[Placa] = []
melhorSequencia: List[Peca] = []

def lerPecas(nomeArq: str) -> List[Peca]:
    pecas: List[Peca] = []
    with open(nomeArq, 'r') as arquivo:
        qtdePeças = int(arquivo.readline())
        for _ in range(qtdePeças):
            altura, comprimento = map(int, arquivo.readline().split())
            pecas.append(Peca(altura=altura, largura=comprimento))
    return pecas


# divide a lógica em duas funções e mantém o nome original chamando ambas
def validarPosicao(pecasAlocadas: Placa, altura: int, largura: int, posicaoX: int, posicaoY: int) -> bool:
    limiteMax = DIMENSAO_PLACA - MARGEM  

    # checa se está dentro dos limites da placa
    if (posicaoX < MARGEM or posicaoY < MARGEM or posicaoX + largura > limiteMax or posicaoY + altura > limiteMax):
        return False

    # verifica sobreposição com peças já alocadas
    for alocada in pecasAlocadas:
        novaPecaX1 = posicaoX
        novaPecaX2 = posicaoX + largura
        novaPecaY1 = posicaoY
        novaPecaY2 = posicaoY + altura

        alocadaX1 = alocada.x
        alocadaX2 = alocada.x + alocada.largura
        alocadaY1 = alocada.y
        alocadaY2 = alocada.y + alocada.altura

        # sobrepõe se intervalos x e y cruzarem
        if novaPecaX1 < alocadaX2 and novaPecaX2 > alocadaX1 and novaPecaY1 < alocadaY2 and novaPecaY2 > alocadaY1:
            return False

    return True


def calcularCustoCorte(pecasAlocadas: Placa, posicaoX: int, posicaoY: int, altura: int, largura: int) -> float:
    perimetro = 2 * (altura + largura)
    arestaEncostada = calcularArestasEncostadas(pecasAlocadas, posicaoX, posicaoY, altura, largura)
    corteUnico = max(0, perimetro - arestaEncostada)
    return corteUnico * CUSTO_POR_CM


def validarPosicaoECalcularCusto(pecasAlocadas: Placa, altura: int, largura: int, posicaoX: int, posicaoY: int) -> Tuple[bool, float]:
    valido = validarPosicao(pecasAlocadas, altura, largura, posicaoX, posicaoY)
    custo = calcularCustoCorte(pecasAlocadas, posicaoX, posicaoY, altura, largura) if valido else 0.0
    return valido, custo

def acharMelhorPosicaoValida(pecasAlocadas: Placa, altura: int, largura: int) -> Tuple[Optional[int], Optional[int], float]:
    limiteMax = DIMENSAO_PLACA - MARGEM
    melhorX = None
    melhorY = None
    melhorCusto = float('inf')
    melhorArestaEncostada = -1
    
    # percorre todas as posições possíveis dentro dos limites
    for y in range(MARGEM, limiteMax):
        if y + altura <= limiteMax:
            for x in range(MARGEM, limiteMax):
                if x + largura <= limiteMax:
                    valido, custoCorte = validarPosicaoECalcularCusto(pecasAlocadas, altura, largura, x, y)
                    if valido:
                        # mede quanto de aresta encosta em outras peças (pra reduzir custo)
                        arestaEncostada = calcularArestasEncostadas(pecasAlocadas, x, y, altura, largura)
                        
                        # escolhe a posição com menor custo ou maior aresta encostada quando empat
                        if custoCorte < melhorCusto or (custoCorte == melhorCusto and arestaEncostada > melhorArestaEncostada):
                            melhorCusto = custoCorte
                            melhorArestaEncostada = arestaEncostada
                            melhorX = x
                            melhorY = y
    
    # retorna a melhor posição encontrada
    if melhorX is not None:
        return melhorX, melhorY, melhorCusto

    # se não encontrou nenhuma válida
    return None, None, 0.0

# calcula o total de bordas que encostam em outras peças (reduz custo de corte)
def calcularArestasEncostadas(pecasAlocadas: Placa, posicaoX: int, posicaoY: int, altura: int, largura: int) -> int:
    totalAresta = 0

    # limites da nova peça
    novaPecaX1 = posicaoX
    novaPecaX2 = posicaoX + largura
    novaPecaY1 = posicaoY
    novaPecaY2 = posicaoY + altura

    # compara com cada peça já alocada
    for alocada in pecasAlocadas:
        ax1 = alocada.x
        ax2 = alocada.x + alocada.largura
        ay1 = alocada.y
        ay2 = alocada.y + alocada.altura

        # soma o tamanho dos lados que encostam 
        if novaPecaX1 == ax2:  # lado esquerdo da nova peça toca no direito da alocada
            overlap = min(novaPecaY2, ay2) - max(novaPecaY1, ay1)
            if overlap > 0:
                totalAresta += overlap
        if novaPecaX2 == ax1:  # lado direito da nova peça toca no esquerdo da alocada
            overlap = min(novaPecaY2, ay2) - max(novaPecaY1, ay1)
            if overlap > 0:
                totalAresta += overlap
        if novaPecaY1 == ay2:  # parte de cima da nova peça toca na parte de baixo da alocada
            overlap = min(novaPecaX2, ax2) - max(novaPecaX1, ax1)
            if overlap > 0:
                totalAresta += overlap
        if novaPecaY2 == ay1:  # parte de baixo da nova peça toca na parte de cima da alocada
            overlap = min(novaPecaX2, ax2) - max(novaPecaX1, ax1)
            if overlap > 0:
                totalAresta += overlap

    return totalAresta


# usa backtracking pra testar todas as combinações de alocação
def buscarMelhorSequencia(pecasParaAlocar: List[Peca], pecasUsadas: List[bool], placasAtuais: List[Placa], custoAtual: float, sequenciaAtual: List[Peca]) -> None:

    global melhorCusto, melhorAlocacao, melhorSequencia

    # caso base: todas as peças foram alocadas
    if len(sequenciaAtual) == len(pecasParaAlocar):
        if custoAtual < melhorCusto:
            melhorCusto = custoAtual
            melhorAlocacao = copy.deepcopy(placasAtuais)
            melhorSequencia = copy.deepcopy(sequenciaAtual)
        return

    for i in range(len(pecasParaAlocar)):
        if not pecasUsadas[i]:
            
            pecasUsadas[i] = True
            pecaAtual = pecasParaAlocar[i]
            altura, largura = pecaAtual.altura, pecaAtual.largura
            
            novaSequencia = sequenciaAtual + [pecaAtual]
            
            posicaoEncontrada = False

            # tenta encaixar nas placas já existentes
            for idPlaca, pecasNaPlaca in enumerate(placasAtuais):
                posX, posY, custoCorte = acharMelhorPosicaoValida(pecasNaPlaca, altura, largura)
                
                if posX is not None: 
                    posicaoEncontrada = True
                    pecaAlocadaInfo = PecaAlocada(x=posX, y=posY, altura=altura, largura=largura)
                    
                    placasAtuais[idPlaca].append(pecaAlocadaInfo)
                    buscarMelhorSequencia(pecasParaAlocar, pecasUsadas, placasAtuais, custoAtual + custoCorte, novaSequencia)
                    placasAtuais[idPlaca].pop() 
                    break 

            # se não couber em nenhuma cria nova
            if not posicaoEncontrada:
                valido, custoCorte = validarPosicaoECalcularCusto([], altura, largura, MARGEM, MARGEM)
                
                if valido: 
                    pecaAlocadaInfo = PecaAlocada(x=MARGEM, y=MARGEM, altura=altura, largura=largura)
                    placasAtuais.append([pecaAlocadaInfo])
                    
                    custoComNovaPlaca = custoAtual + custoCorte + CUSTO_PLACA
                    buscarMelhorSequencia(pecasParaAlocar, pecasUsadas, placasAtuais, custoComNovaPlaca, novaSequencia)
                    
                    placasAtuais.pop() 

            pecasUsadas[i] = False


def resolverForcaBruta(pecas: List[Peca]) -> Tuple[List[Placa], float, float]:

    global melhorCusto, melhorAlocacao, melhorSequencia
    
    melhorCusto = float('inf')
    melhorAlocacao = []
    melhorSequencia = []

    # marca quais peças já foram usadas na busca (começa com todas como false)
    pecasUsadas: List[bool] = [False] * len(pecas)

    placasAtuais: List[Placa] = [] 
    custoAtual: float = 0.0
    sequenciaAtual: List[Peca] = [] 
    
    inicio = time.time()    
    buscarMelhorSequencia(pecas, pecasUsadas, placasAtuais, custoAtual, sequenciaAtual)
    fim = time.time()

    tempoTotal = fim - inicio
    
    return melhorAlocacao, melhorCusto, tempoTotal

