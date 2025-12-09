#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define NUM_MOLDURAS 8
#define NUM_PAGINAS 16

// ============== ESTRUTURAS DE DADOS ==============

typedef struct {
    bool presente;
    int moldura;
    bool referenciada;
    bool modificada;
} Pagina;

// ============== VARIÁVEIS GLOBAIS ==============

Pagina tabela_paginas[NUM_PAGINAS];
int memoria_fisica[NUM_MOLDURAS];  // -1 = vazio, senão ID da página

// ============== FUNÇÕES ==============

void inicializar() {
    // Inicializa tudo como falso/vazio
    for (int i = 0; i < NUM_PAGINAS; i++) {
        tabela_paginas[i].presente = false;
        tabela_paginas[i].moldura = -1;
        tabela_paginas[i].referenciada = false;
        tabela_paginas[i].modificada = false;
    }
    
    for (int i = 0; i < NUM_MOLDURAS; i++) {
        memoria_fisica[i] = -1;
    }
    
    // Mapeamento inicial (da figura)
    int mapeamento[][2] = {
        {2, 0}, {1, 1}, {6, 2}, {0, 3},
        {4, 4}, {3, 5}, {5, 6}, {7, 7}
    };
    
    int num_mapeamentos = 8;
    
    for (int i = 0; i < num_mapeamentos; i++) {
        int pagina = mapeamento[i][0];
        int moldura = mapeamento[i][1];
        
        tabela_paginas[pagina].presente = true;
        tabela_paginas[pagina].moldura = moldura;
        tabela_paginas[pagina].referenciada = true;  // Todas referenciadas
        tabela_paginas[pagina].modificada = false;
        memoria_fisica[moldura] = pagina;
    }
}

void imprimir_estado() {
    printf("\n=== ESTADO ATUAL ===\n");
    printf("Memória física:\n");
    for (int i = 0; i < NUM_MOLDURAS; i++) {
        printf("  Moldura %d: Página %d\n", i, memoria_fisica[i]);
    }
    
    printf("\nPáginas presentes:\n");
    for (int i = 0; i < NUM_PAGINAS; i++) {
        if (tabela_paginas[i].presente) {
            printf("  Página %d: Moldura %d, R=%d, M=%d\n",
                   i, tabela_paginas[i].moldura,
                   tabela_paginas[i].referenciada,
                   tabela_paginas[i].modificada);
        }
    }
}

// ============== ALGORITMO FIFO EM C ==============

void simulador_fifo() {
    printf("=== SIMULANDO ALGORITMO FIFO ===\n");
    
    // Sequência de acessos
    char operacoes[] = {'R', 'R', 'M', 'R', 'M', 'M', 'R', 'R', 'R', 'R',
                        'M', 'R', 'R', 'M', 'R', 'R', 'R', 'M', 'R', 'R',
                        'R', 'M', 'R', 'R', 'R'};
    int paginas[] = {0, 1, 2, 6, 7, 1, 7, 6, 2, 3,
                     0, 4, 0, 6, 1, 8, 12, 8, 2, 15,
                     6, 0, 3, 5, 0};
    
    int num_acessos = 25;
    int hits = 0, misses = 0;
    
    // Fila FIFO (simples com array)
    int fila[NUM_MOLDURAS];
    int inicio_fila = 0;
    int fim_fila = 0;
    
    // Inicializa fila com páginas iniciais
    for (int i = 0; i < NUM_MOLDURAS; i++) {
        if (memoria_fisica[i] != -1) {
            fila[fim_fila++] = memoria_fisica[i];
        }
    }
    
    // Processa cada acesso
    for (int i = 0; i < num_acessos; i++) {
        char op = operacoes[i];
        int pagina = paginas[i];
        
        printf("\n--- Acesso %d: (%c) Página %d ---\n", i+1, op, pagina);
        
        if (tabela_paginas[pagina].presente) {
            hits++;
            printf("  -> HIT! Pagina já esta na memoria (moldura %d)\n",
                   tabela_paginas[pagina].moldura);
        } else {
            misses++;
            printf("  -> MISS! Pagina nao esta na memoria\n");
            
            int moldura_livre = -1;
            
            // Procura moldura livre
            for (int m = 0; m < NUM_MOLDURAS; m++) {
                if (memoria_fisica[m] == -1) {
                    moldura_livre = m;
                    break;
                }
            }
            
            // Se não tem moldura livre, precisa substituir
            if (moldura_livre == -1) {
                // FIFO: pega a primeira da fila
                int pagina_remover = fila[inicio_fila++];
                inicio_fila %= NUM_MOLDURAS;  // Circular 
                
                moldura_livre = tabela_paginas[pagina_remover].moldura;
                
                printf("  -> Substituindo página %d (moldura %d)\n",
                       pagina_remover, moldura_livre);
                
                if (tabela_paginas[pagina_remover].modificada) {
                    printf("  -> AVISO: Página %d foi modificada! (Precisa salvar)\n",
                           pagina_remover);
                }
                
                // Remove página antiga
                tabela_paginas[pagina_remover].presente = false;
                tabela_paginas[pagina_remover].referenciada = false;
                tabela_paginas[pagina_remover].modificada = false;
                tabela_paginas[pagina_remover].moldura = -1;
            } else {
                printf("  -> Moldura %d está livre\n", moldura_livre);
            }
            
            // Coloca nova página
            tabela_paginas[pagina].presente = true;
            tabela_paginas[pagina].moldura = moldura_livre;
            memoria_fisica[moldura_livre] = pagina;
            
            // Adiciona na fila
            fila[fim_fila++] = pagina;
            fim_fila %= NUM_MOLDURAS;
        }
        
        // Atualiza bits
        tabela_paginas[pagina].referenciada = true;
        if (op == 'M') {
            tabela_paginas[pagina].modificada = true;
            printf("  -> Página %d marcada como MODIFICADA (M=1)\n", pagina);
        }
        
        // Para ver todos os estados, descomente:
        // imprimir_estado();
    }
    
    // Resultados
    printf("\n========================================\n");
    printf("RESULTADOS FIFO:\n");
    printf("Total de acessos: %d\n", num_acessos);
    printf("HITS: %d (%.1f%%)\n", hits, (float)hits/num_acessos*100);
    printf("MISSES: %d (%.1f%%)\n", misses, (float)misses/num_acessos*100);
    printf("========================================\n");
}

// ============== MAIN ==============

int main() {
    printf("SIMULADOR DE GERENCIAMENTO DE MEMÓRIA\n");
    printf("Memória: 32KB física, 64KB virtual\n");
    printf("Páginas: 4KB, 8 molduras físicas, 16 páginas virtuais\n");
    
    inicializar();
    imprimir_estado();
    
    simulador_fifo();
    
    return 0;
}