import copy

NUM_MOLDURAS = 8
NUM_PAGINAS = 16

# Memória física tem 8 molduras (0 a 7)
memoria_fisica = [None] * NUM_MOLDURAS  # None = vazio, senão guarda o ID da página

# Tabela de páginas: 16 páginas virtuais (0 a 15)
# Cada página tem: [presente, moldura, referenciada, modificada, tempo_carga, ultimo_acesso]
tabela_paginas = []
for i in range(NUM_PAGINAS):
    tabela_paginas.append({
        'presente': False,
        'moldura': -1,
        'referenciada': False,
        'modificada': False,
        'tempo_carga': -1,      # Para FIFO/MRU
        'ultimo_acesso': -1     # Para MRU/LRU
    })

# Mapeamento inicial: {pagina: moldura}
mapeamento_inicial = {
    2: 0,  # Página 2 na moldura 0
    1: 1,  # Página 1 na moldura 1
    6: 2,  # Página 6 na moldura 2
    0: 3,  # Página 0 na moldura 3
    4: 4,  # Página 4 na moldura 4
    3: 5,  # Página 3 na moldura 5
    5: 6,  # Página 5 na moldura 6
    7: 7   # Página 7 na moldura 7
}

# Sequência de acessos
sequencia = [
    ('R', 0), ('R', 1), ('M', 2), ('R', 6), ('M', 7),
    ('M', 1), ('R', 7), ('R', 6), ('R', 2), ('R', 3),
    ('M', 0), ('R', 4), ('R', 0), ('M', 6), ('R', 1),
    ('R', 8), ('R', 12), ('M', 8), ('R', 2), ('R', 15),
    ('R', 6), ('M', 0), ('R', 3), ('R', 5), ('R', 0)
]

# ============== FUNÇÕES AUXILIARES ==============

def inicializar_sistema():
    """Inicializa a memória com o estado inicial"""
    global memoria_fisica, tabela_paginas
    
    # Limpa tudo
    memoria_fisica = [None] * NUM_MOLDURAS
    for i in range(NUM_PAGINAS):
        tabela_paginas[i]['presente'] = False
        tabela_paginas[i]['moldura'] = -1
        tabela_paginas[i]['referenciada'] = False
        tabela_paginas[i]['modificada'] = False
        tabela_paginas[i]['tempo_carga'] = -1
        tabela_paginas[i]['ultimo_acesso'] = -1
    
    # Aplica o mapeamento inicial
    tempo = 0
    for pagina, moldura in mapeamento_inicial.items():
        tabela_paginas[pagina]['presente'] = True
        tabela_paginas[pagina]['moldura'] = moldura
        tabela_paginas[pagina]['referenciada'] = True
        tabela_paginas[pagina]['modificada'] = False
        tabela_paginas[pagina]['tempo_carga'] = tempo
        tabela_paginas[pagina]['ultimo_acesso'] = tempo
        memoria_fisica[moldura] = pagina
        tempo += 1

def imprimir_estado():
    """Mostra o estado atual da memória"""
    print("\n" + "="*60)
    print("MEMÓRIA FÍSICA (8 molduras):")
    for i in range(NUM_MOLDURAS):
        pagina = memoria_fisica[i]
        if pagina is not None:
            estado = f"Página {pagina}"
            if tabela_paginas[pagina]['modificada']:
                estado += " [M]"
            if tabela_paginas[pagina]['referenciada']:
                estado += " [R]"
            print(f"  Moldura {i}: {estado}")
        else:
            print(f"  Moldura {i}: Vazia")
    
    print("\nPÁGINAS PRESENTES NA MEMÓRIA:")
    for i in range(NUM_PAGINAS):
        if tabela_paginas[i]['presente']:
            print(f"  Página {i}: Moldura {tabela_paginas[i]['moldura']}, "
                  f"R={tabela_paginas[i]['referenciada']}, "
                  f"M={tabela_paginas[i]['modificada']}, "
                  f"Tempo={tabela_paginas[i]['tempo_carga']}")

def encontrar_moldura_livre():
    """Encontra uma moldura livre, retorna -1 se não houver"""
    for i in range(NUM_MOLDURAS):
        if memoria_fisica[i] is None:
            return i
    return -1

# ============== ALGORITMO NUR (Não Usada Recentemente) ==============

def escolher_vitima_nur():
    """Escolhe uma vítima usando algoritmo NUR"""
    # Classe 1: R=0, M=0 (melhor caso)
    for pagina in range(NUM_PAGINAS):
        if (tabela_paginas[pagina]['presente'] and 
            not tabela_paginas[pagina]['referenciada'] and 
            not tabela_paginas[pagina]['modificada']):
            return pagina
    
    # Classe 2: R=0, M=1
    for pagina in range(NUM_PAGINAS):
        if (tabela_paginas[pagina]['presente'] and 
            not tabela_paginas[pagina]['referenciada'] and 
            tabela_paginas[pagina]['modificada']):
            return pagina
    
    # Classe 3: R=1, M=0
    for pagina in range(NUM_PAGINAS):
        if (tabela_paginas[pagina]['presente'] and 
            tabela_paginas[pagina]['referenciada'] and 
            not tabela_paginas[pagina]['modificada']):
            return pagina
    
    # Classe 4: R=1, M=1 (último caso)
    for pagina in range(NUM_PAGINAS):
        if tabela_paginas[pagina]['presente']:
            return pagina
    
    return 0  # Fallback

def simulador_nur():
    """Simula o algoritmo NUR"""
    print("\n" + "="*60)
    print("ALGORITMO: NÃO USADA RECENTEMENTE (NUR)")
    print("="*60)
    
    inicializar_sistema()
    hits = 0
    misses = 0
    tempo = len(mapeamento_inicial)  # Começa após as páginas iniciais
    
    for i, (op, pagina) in enumerate(sequencia):
        print(f"\n--- Acesso {i+1}/25: ({op}) Página {pagina} ---")
        
        # Verifica se está na memória
        if tabela_paginas[pagina]['presente']:
            hits += 1
            print(f"  → HIT! Página {pagina} já está na memória")
        else:
            misses += 1
            print(f"  → MISS! Página {pagina} não está na memória")
            
            moldura_livre = encontrar_moldura_livre()
            
            if moldura_livre == -1:
                # Memória cheia, precisa substituir
                vitima = escolher_vitima_nur()
                moldura_livre = tabela_paginas[vitima]['moldura']
                
                print(f"  → Substituindo Página {vitima} (moldura {moldura_livre})")
                
                if tabela_paginas[vitima]['modificada']:
                    print(f"  ⚠️  Página {vitima} foi MODIFICADA! (Precisa salvar no disco)")
                
                # Remove a página antiga
                tabela_paginas[vitima]['presente'] = False
                tabela_paginas[vitima]['referenciada'] = False
                tabela_paginas[vitima]['modificada'] = False
                tabela_paginas[vitima]['moldura'] = -1
            else:
                print(f"  → Usando moldura livre {moldura_livre}")
            
            # Coloca a nova página
            tabela_paginas[pagina]['presente'] = True
            tabela_paginas[pagina]['moldura'] = moldura_livre
            tabela_paginas[pagina]['tempo_carga'] = tempo
            memoria_fisica[moldura_livre] = pagina
        
        # Atualiza bits
        tabela_paginas[pagina]['referenciada'] = True
        tabela_paginas[pagina]['ultimo_acesso'] = tempo
        
        if op == 'M':
            tabela_paginas[pagina]['modificada'] = True
            print(f"  → Página {pagina} marcada como MODIFICADA")
        
        # A cada 4 acessos, reseta os bits R (simulando limpeza periódica)
        if (i + 1) % 4 == 0:
            for p in range(NUM_PAGINAS):
                if tabela_paginas[p]['presente']:
                    tabela_paginas[p]['referenciada'] = False
        
        tempo += 1
    
    return hits, misses

# ============== ALGORITMO FIFO ==============

def simulador_fifo():
    """Simula o algoritmo FIFO"""
    print("\n" + "="*60)
    print("ALGORITMO: PRIMEIRA A ENTRAR, PRIMEIRA A SAIR (FIFO)")
    print("="*60)
    
    inicializar_sistema()
    hits = 0
    misses = 0
    tempo = len(mapeamento_inicial)
    
    # Fila FIFO (mantém ordem de chegada)
    fila_fifo = list(mapeamento_inicial.keys())
    
    for i, (op, pagina) in enumerate(sequencia):
        print(f"\n--- Acesso {i+1}/25: ({op}) Página {pagina} ---")
        
        if tabela_paginas[pagina]['presente']:
            hits += 1
            print(f"  → HIT! Página {pagina} já está na memória")
        else:
            misses += 1
            print(f"  → MISS! Página {pagina} não está na memória")
            
            moldura_livre = encontrar_moldura_livre()
            
            if moldura_livre == -1:
                # FIFO: remove a primeira da fila
                vitima = fila_fifo.pop(0)
                moldura_livre = tabela_paginas[vitima]['moldura']
                
                print(f"  → Substituindo Página {vitima} (moldura {moldura_livre})")
                
                if tabela_paginas[vitima]['modificada']:
                    print(f"  ⚠️  Página {vitima} foi MODIFICADA!")
                
                # Remove a página antiga
                tabela_paginas[vitima]['presente'] = False
                tabela_paginas[vitima]['referenciada'] = False
                tabela_paginas[vitima]['modificada'] = False
                tabela_paginas[vitima]['moldura'] = -1
            else:
                print(f"  → Usando moldura livre {moldura_livre}")
            
            # Coloca a nova página
            tabela_paginas[pagina]['presente'] = True
            tabela_paginas[pagina]['moldura'] = moldura_livre
            tabela_paginas[pagina]['tempo_carga'] = tempo
            memoria_fisica[moldura_livre] = pagina
            fila_fifo.append(pagina)  # Adiciona no final
        
        # Atualiza bits
        tabela_paginas[pagina]['referenciada'] = True
        tabela_paginas[pagina]['ultimo_acesso'] = tempo
        
        if op == 'M':
            tabela_paginas[pagina]['modificada'] = True
            print(f"  → Página {pagina} marcada como MODIFICADA")
        
        tempo += 1
    
    return hits, misses

# ============== ALGORITMO SEGUNDA CHANCE (SC) ==============

def simulador_segunda_chance():
    """Simula o algoritmo Segunda Chance"""
    print("\n" + "="*60)
    print("ALGORITMO: SEGUNDA CHANCE (SC)")
    print("="*60)
    
    inicializar_sistema()
    hits = 0
    misses = 0
    tempo = len(mapeamento_inicial)
    
    # Fila para Segunda Chance
    fila_sc = list(mapeamento_inicial.keys())
    
    for i, (op, pagina) in enumerate(sequencia):
        print(f"\n--- Acesso {i+1}/25: ({op}) Página {pagina} ---")
        
        if tabela_paginas[pagina]['presente']:
            hits += 1
            print(f"  → HIT! Página {pagina} já está na memória")
        else:
            misses += 1
            print(f"  → MISS! Página {pagina} não está na memória")
            
            moldura_livre = encontrar_moldura_livre()
            
            if moldura_livre == -1:
                # Segunda Chance: procura vítima
                while True:
                    candidata = fila_sc.pop(0)
                    
                    if tabela_paginas[candidata]['referenciada']:
                        # Dá segunda chance
                        print(f"  → Dando SEGUNDA CHANCE para Página {candidata} (R=1)")
                        tabela_paginas[candidata]['referenciada'] = False
                        fila_sc.append(candidata)
                    else:
                        # Esta é a vítima
                        vitima = candidata
                        moldura_livre = tabela_paginas[vitima]['moldura']
                        print(f"  → Substituindo Página {vitima} (moldura {moldura_livre})")
                        
                        if tabela_paginas[vitima]['modificada']:
                            print(f"  ⚠️  Página {vitima} foi MODIFICADA!")
                        
                        # Remove a página antiga
                        tabela_paginas[vitima]['presente'] = False
                        tabela_paginas[vitima]['referenciada'] = False
                        tabela_paginas[vitima]['modificada'] = False
                        tabela_paginas[vitima]['moldura'] = -1
                        break
            else:
                print(f"  → Usando moldura livre {moldura_livre}")
            
            # Coloca a nova página
            tabela_paginas[pagina]['presente'] = True
            tabela_paginas[pagina]['moldura'] = moldura_livre
            tabela_paginas[pagina]['tempo_carga'] = tempo
            memoria_fisica[moldura_livre] = pagina
            fila_sc.append(pagina)
        
        # Atualiza bits
        tabela_paginas[pagina]['referenciada'] = True
        tabela_paginas[pagina]['ultimo_acesso'] = tempo
        
        if op == 'M':
            tabela_paginas[pagina]['modificada'] = True
            print(f"  → Página {pagina} marcada como MODIFICADA")
        
        tempo += 1
    
    return hits, misses

# ============== ALGORITMO RELÓGIO ==============

def simulador_relogio():
    """Simula o algoritmo do Relógio"""
    print("\n" + "="*60)
    print("ALGORITMO: RELÓGIO (CLOCK)")
    print("="*60)
    
    inicializar_sistema()
    hits = 0
    misses = 0
    tempo = len(mapeamento_inicial)
    
    # Lista de páginas na memória (para o ponteiro do relógio)
    paginas_na_memoria = list(mapeamento_inicial.keys())
    ponteiro = 0  # Ponteiro do relógio
    
    for i, (op, pagina) in enumerate(sequencia):
        print(f"\n--- Acesso {i+1}/25: ({op}) Página {pagina} ---")
        
        if tabela_paginas[pagina]['presente']:
            hits += 1
            print(f"  → HIT! Página {pagina} já está na memória")
        else:
            misses += 1
            print(f"  → MISS! Página {pagina} não está na memória")
            
            moldura_livre = encontrar_moldura_livre()
            
            if moldura_livre == -1:
                # Algoritmo do Relógio
                while True:
                    candidata_idx = ponteiro % len(paginas_na_memoria)
                    candidata = paginas_na_memoria[candidata_idx]
                    
                    if tabela_paginas[candidata]['referenciada']:
                        # Dá segunda chance (marca R=0 e avança)
                        print(f"  → Relógio: Página {candidata} tem R=1, marcando como 0")
                        tabela_paginas[candidata]['referenciada'] = False
                        ponteiro += 1
                    else:
                        # Encontrou vítima (R=0)
                        vitima = candidata
                        moldura_livre = tabela_paginas[vitima]['moldura']
                        
                        print(f"  → Substituindo Página {vitima} (moldura {moldura_livre})")
                        
                        if tabela_paginas[vitima]['modificada']:
                            print(f"  ⚠️  Página {vitima} foi MODIFICADA!")
                        
                        # Remove da lista
                        paginas_na_memoria.pop(candidata_idx)
                        
                        # Remove a página antiga
                        tabela_paginas[vitima]['presente'] = False
                        tabela_paginas[vitima]['referenciada'] = False
                        tabela_paginas[vitima]['modificada'] = False
                        tabela_paginas[vitima]['moldura'] = -1
                        break
            else:
                print(f"  → Usando moldura livre {moldura_livre}")
            
            # Coloca a nova página
            tabela_paginas[pagina]['presente'] = True
            tabela_paginas[pagina]['moldura'] = moldura_livre
            tabela_paginas[pagina]['tempo_carga'] = tempo
            memoria_fisica[moldura_livre] = pagina
            paginas_na_memoria.append(pagina)
        
        # Atualiza bits
        tabela_paginas[pagina]['referenciada'] = True
        tabela_paginas[pagina]['ultimo_acesso'] = tempo
        
        if op == 'M':
            tabela_paginas[pagina]['modificada'] = True
            print(f"  → Página {pagina} marcada como MODIFICADA")
        
        tempo += 1
    
    return hits, misses

# ============== ALGORITMO MRU ==============

def simulador_mru():
    """Simula o algoritmo MRU (Mais Recentemente Usado)"""
    print("\n" + "="*60)
    print("ALGORITMO: MAIS RECENTEMENTE USADO (MRU)")
    print("="*60)
    
    inicializar_sistema()
    hits = 0
    misses = 0
    tempo = len(mapeamento_inicial)
    
    for i, (op, pagina) in enumerate(sequencia):
        print(f"\n--- Acesso {i+1}/25: ({op}) Página {pagina} ---")
        
        if tabela_paginas[pagina]['presente']:
            hits += 1
            print(f"  → HIT! Página {pagina} já está na memória")
        else:
            misses += 1
            print(f"  → MISS! Página {pagina} não está na memória")
            
            moldura_livre = encontrar_moldura_livre()
            
            if moldura_livre == -1:
                # MRU: encontra a página com maior ultimo_acesso
                max_tempo = -1
                vitima = -1
                
                for p in range(NUM_PAGINAS):
                    if tabela_paginas[p]['presente']:
                        if tabela_paginas[p]['ultimo_acesso'] > max_tempo:
                            max_tempo = tabela_paginas[p]['ultimo_acesso']
                            vitima = p
                
                moldura_livre = tabela_paginas[vitima]['moldura']
                print(f"  → Substituindo Página {vitima} (usada mais recentemente em t={max_tempo})")
                
                if tabela_paginas[vitima]['modificada']:
                    print(f"  ⚠️  Página {vitima} foi MODIFICADA!")
                
                # Remove a página antiga
                tabela_paginas[vitima]['presente'] = False
                tabela_paginas[vitima]['referenciada'] = False
                tabela_paginas[vitima]['modificada'] = False
                tabela_paginas[vitima]['moldura'] = -1
            else:
                print(f"  → Usando moldura livre {moldura_livre}")
            
            # Coloca a nova página
            tabela_paginas[pagina]['presente'] = True
            tabela_paginas[pagina]['moldura'] = moldura_livre
            tabela_paginas[pagina]['tempo_carga'] = tempo
            memoria_fisica[moldura_livre] = pagina
        
        # Atualiza bits
        tabela_paginas[pagina]['referenciada'] = True
        tabela_paginas[pagina]['ultimo_acesso'] = tempo
        
        if op == 'M':
            tabela_paginas[pagina]['modificada'] = True
            print(f"  → Página {pagina} marcada como MODIFICADA")
        
        tempo += 1
    
    return hits, misses

# ============== EXECUTAR TODOS OS ALGORITMOS ==============

def executar_todos_algoritmos():
    """Executa todos os 5 algoritmos e mostra resultados comparativos"""
    print("="*80)
    print("SIMULADOR DE GERENCIAMENTO DE MEMÓRIA VIRTUAL")
    print("="*80)
    print(f"Configuração: 32KB física, 64KB virtual, páginas de 4KB")
    print(f"8 molduras físicas, 16 páginas virtuais")
    print(f"25 acessos na sequência")
    print("="*80)
    
    resultados = []
    
    # Executa cada algoritmo
    algoritmos = [
        ("NUR", simulador_nur),
        ("FIFO", simulador_fifo),
        ("Segunda Chance", simulador_segunda_chance),
        ("Relógio", simulador_relogio),
        ("MRU", simulador_mru)
    ]
    
    for nome, algoritmo in algoritmos:
        print(f"\n\n{'='*60}")
        print(f"EXECUTANDO: {nome}")
        print('='*60)
        hits, misses = algoritmo()
        resultados.append((nome, hits, misses))
    
    # Tabela comparativa
    print("\n" + "="*80)
    print("RESULTADOS COMPARATIVOS")
    print("="*80)
    print(f"{'ALGORITMO':<20} {'HITS':<8} {'MISSES':<8} {'TAXA DE HIT':<12} {'TAXA DE MISS':<12}")
    print("-"*80)
    
    for nome, hits, misses in resultados:
        total = hits + misses
        taxa_hit = (hits / total) * 100 if total > 0 else 0
        taxa_miss = (misses / total) * 100 if total > 0 else 0
        print(f"{nome:<20} {hits:<8} {misses:<8} {taxa_hit:>10.1f}% {taxa_miss:>10.1f}%")
    
    # Encontra o melhor algoritmo
    melhor = max(resultados, key=lambda x: x[1])  # Maior número de hits
    print("\n" + "="*80)
    print(f"🏆 MELHOR ALGORITMO: {melhor[0]} com {melhor[1]} hits ({melhor[1]/25*100:.1f}%)")
    print("="*80)
    
    return resultados

# ============== MENU INTERATIVO ==============

def menu_interativo():
    """Menu para escolher qual algoritmo executar"""
    while True:
        print("\n" + "="*60)
        print("MENU DO SIMULADOR")
        print("="*60)
        print("1. Executar TODOS os algoritmos (comparativo)")
        print("2. Executar NUR (Não Usada Recentemente)")
        print("3. Executar FIFO (Primeira a Entrar, Primeira a Sair)")
        print("4. Executar Segunda Chance")
        print("5. Executar Relógio")
        print("6. Executar MRU (Mais Recentemente Usado)")
        print("7. Ver estado inicial da memória")
        print("8. Sair")
        print("="*60)
        
        escolha = input("Escolha uma opção (1-8): ").strip()
        
        if escolha == '1':
            executar_todos_algoritmos()
        elif escolha == '2':
            hits, misses = simulador_nur()
            print_resultado("NUR", hits, misses)
        elif escolha == '3':
            hits, misses = simulador_fifo()
            print_resultado("FIFO", hits, misses)
        elif escolha == '4':
            hits, misses = simulador_segunda_chance()
            print_resultado("Segunda Chance", hits, misses)
        elif escolha == '5':
            hits, misses = simulador_relogio()
            print_resultado("Relógio", hits, misses)
        elif escolha == '6':
            hits, misses = simulador_mru()
            print_resultado("MRU", hits, misses)
        elif escolha == '7':
            inicializar_sistema()
            imprimir_estado()
        elif escolha == '8':
            print("Encerrando simulador...")
            break
        else:
            print("Opção inválida! Tente novamente.")

def print_resultado(nome, hits, misses):
    """Imprime resultados de um algoritmo"""
    print("\n" + "="*60)
    print(f"RESULTADO: {nome}")
    print("="*60)
    print(f"Total de acessos: 25")
    print(f"HITS: {hits} ({hits/25*100:.1f}%)")
    print(f"MISSES: {misses} ({misses/25*100:.1f}%)")
    print("="*60)

# ============== EXECUÇÃO PRINCIPAL ==============

if __name__ == "__main__":
    print("Bem-vindo ao Simulador de Gerenciamento de Memória!")
    print("Este simulador implementa 5 algoritmos de substituição de páginas.")
    
    # Inicializa o sistema
    inicializar_sistema()
    
    # Executa o menu interativo
    menu_interativo()
    
    print("\nSimulação concluída! Use os resultados para seu relatório.")