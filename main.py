import copy
import time
import sys
from collections import namedtuple 
from typing import List, Tuple, Optional

CUSTO_PLACA = 1000.00
CUSTO_POR_CM = 0.01
MARGEM = 10 
DIMENSAO_PLACA = 300
DIMENSAO_FINAL = DIMENSAO_PLACA - 2 * MARGEM #280 cm


Peca = namedtuple("Peca", ["altura", "largura"]) 
PecaAlocada = namedtuple("PecaAlocada", ["x", "y", "altura", "largura"])

Placa = List[PecaAlocada]

melhorCusto: float = float('inf') # inf=infinito p/ começar com maior valor possível pra depois minimizar
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

def validarPosicaoECalcularCusto(pecasAlocadas: Placa, altura: int, largura: int, 
                                 posicaoX: int, posicaoY: int) -> Tuple[bool, float]:
    limiteMax = DIMENSAO_PLACA - MARGEM  

    if (posicaoX < MARGEM or 
        posicaoY < MARGEM or 
        posicaoX + largura > limiteMax or 
        posicaoY + altura > limiteMax):
        return False, 0.0

    for alocada in pecasAlocadas:
        
        # limites da nova peça
        novaX1 = posicaoX
        novaX2 = posicaoX + largura
        novaY1 = posicaoY
        novaY2 = posicaoY + altura

        # limites da peça alocada 
        alocadaX1 = alocada.x
        alocadaX2 = alocada.x + alocada.largura
        alocadaY1 = alocada.y
        alocadaY2 = alocada.y + alocada.altura

        # sobrepõe se os intervalos x e y cruzarem 
        if novaX1 < alocadaX2 and novaX2 > alocadaX1 and novaY1 < alocadaY2 and novaY2 > alocadaY1:
            return False, 0.0

    perimetro = 2 * (altura + largura)
    custoCorte = perimetro * CUSTO_POR_CM
    return True, custoCorte

def qualPrimeiraPosicaoValida(pecasAlocadas: Placa, altura: int, largura: int) -> Tuple[Optional[int], Optional[int], float]:
    limiteMax = DIMENSAO_PLACA - MARGEM
    
    for y in range(MARGEM, limiteMax):
        if y + altura <= limiteMax:
            for x in range(MARGEM, limiteMax):
                if x + largura <= limiteMax:
                    valido, custoCorte = validarPosicaoECalcularCusto(pecasAlocadas, altura, largura, x, y)
                    if valido:
                        return x, y, custoCorte
    
    return None, None, 0.0

def backtracking(pecasParaAlocar: List[Peca], pecasUsadas: List[bool], 
                 placasAtuais: List[Placa], custoAtual: float, 
                 sequenciaAtual: List[Peca]) -> None:

    global melhorCusto, melhorAlocacao, melhorSequencia

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
            idPlacaAlocada = -1
            pecaAlocadaInfo = None
            custoDoCorte = 0.0

            for idPlaca, pecasNaPlaca in enumerate(placasAtuais):
                posX, posY, custoCorte = qualPrimeiraPosicaoValida(pecasNaPlaca, altura, largura)
                
                if posX is not None: 
                    posicaoEncontrada = True
                    idPlacaAlocada = idPlaca
                    
                    pecaAlocadaInfo = PecaAlocada(x=posX, y=posY, altura=altura, largura=largura)
                    custoDoCorte = custoCorte
                    
                    placasAtuais[idPlaca].append(pecaAlocadaInfo)
                    
                    backtracking(pecasParaAlocar, pecasUsadas, placasAtuais, custoAtual + custoDoCorte, novaSequencia)
                    
                    placasAtuais[idPlaca].pop() 
                    break 

            if not posicaoEncontrada:
                valido, custoCorte = validarPosicaoECalcularCusto([], altura, largura, MARGEM, MARGEM)
                
                if valido: 
                    pecaAlocadaInfo = PecaAlocada(x=MARGEM, y=MARGEM, altura=altura, largura=largura)
                    custoDoCorte = custoCorte
                    
                    placasAtuais.append([pecaAlocadaInfo])
                    
                    custoComNovaPlaca = custoAtual + custoDoCorte + CUSTO_PLACA
                    backtracking(pecasParaAlocar, pecasUsadas, placasAtuais, custoComNovaPlaca, novaSequencia)
                    
                    placasAtuais.pop() 

            pecasUsadas[i] = False

def forcaBruta(pecas: List[Peca]) -> Tuple[List[Placa], float, float]:

    global melhorCusto, melhorAlocacao, melhorSequencia
    
    melhorCusto = float('inf')
    melhorAlocacao = []
    melhorSequencia = []

    pecasUsadas: List[bool] = [False] * len(pecas)
    placasAtuais: List[Placa] = [] 
    custoAtual: float = 0.0
    sequenciaAtual: List[Peca] = [] 
    
    inicioTempo = time.time()

    backtracking(pecas, pecasUsadas, placasAtuais, custoAtual, sequenciaAtual)

    fimTempo = time.time()
    tempoTotal = fimTempo - inicioTempo
    
    return melhorAlocacao, melhorCusto, tempoTotal