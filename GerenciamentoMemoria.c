#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define NUM_FRAMES 8
#define NUM_PAGINAS 16

typedef enum {NUR, FIFO, SECOND_CHANCE, CLOCK_ALG, MRU} Algorithm;


typedef struct PTE{
    int pagina;
    int presente;
    int modificada;
    int referenciada;
    int moldura;
    int tempo_carregada;
    int ultimo_uso;
} PTE;

typedef struct Frame {
    int pagina;
    int ordem_carregamento;
} Frame;

PTE tabela_paginas[NUM_PAGINAS];
Frame frames[NUM_FRAMES];

int tempo_global = 0;
int ponteiro_clock = 0;
int ponteiro_sc = 0;

int paginas_iniciais[NUM_FRAMES] = {3,1,0,5,4,9,2,11};


void inicializar() {
    tempo_global = 0;
    ponteiro_sc = 0;
    ponteiro_clock = 0;

    for (int i = 0; i < NUM_PAGINAS; i++) {
        tabela_paginas[i].pagina = i;
        tabela_paginas[i].presente = 0;
        tabela_paginas[i].modificada = 0;
        tabela_paginas[i].referenciada = 0;
        tabela_paginas[i].moldura = -1;
        tabela_paginas[i].tempo_carregada = -1;
        tabela_paginas[i].ultimo_uso = -1;
    }

    for (int i = 0; i < NUM_FRAMES; i++) {
        int p = paginas_iniciais[i];
        frames[i].pagina = p;
        frames[i].ordem_carregamento = tempo_global;
        tabela_paginas[p].presente = 1;
        tabela_paginas[p].moldura = i;
        tabela_paginas[p].referenciada = 1;
        tabela_paginas[p].tempo_carregada = tempo_global;
        tabela_paginas[p].ultimo_uso = tempo_global;
        tempo_global++;
    }
}


/*--INICIO FIFO--*/
int vitima_fifo(){
    int indice = 0;
    int menor = INT_MAX;

    for (int i = 0; i < NUM_FRAMES; i++) {
        int pg = frames[i].pagina;
        int tempo = tabela_paginas[pg].tempo_carregada;

        if (tempo < menor) {
            menor = tempo;
            indice = i;
        }
    }

    return indice;
}

void carregar_pagina(int frame, int pagina) {
    int antiga = frames[frame].pagina;

    if (antiga != -1) {
        tabela_paginas[antiga].presente = 0;
        tabela_paginas[antiga].moldura = -1;
        tabela_paginas[antiga].referenciada = 0;
    }

    frames[frame].pagina = pagina;
    frames[frame].ordem_carregamento = tempo_global;

    tabela_paginas[pagina].presente = 1;
    tabela_paginas[pagina].moldura = frame;
    tabela_paginas[pagina].referenciada = 1;
    tabela_paginas[pagina].modificada = 0;
    tabela_paginas[pagina].tempo_carregada = tempo_global;
    tabela_paginas[pagina].ultimo_uso = tempo_global;

    tempo_global++;
}

void acessar_pagina(int pagina, int escrita, int *hits, int *misses) {
    if (tabela_paginas[pagina].presente) {
        (*hits)++;
        tabela_paginas[pagina].referenciada = 1;
        if (escrita) tabela_paginas[pagina].modificada = 1;
        tabela_paginas[pagina].ultimo_uso = tempo_global;
        tempo_global++;
        return;
    }

    (*misses)++;

    int frame = vitima_fifo();
    carregar_pagina(frame, pagina);

    if (escrita) tabela_paginas[pagina].modificada = 1;
}

void executar_FIFO(int acessos[][2], int n){
    inicializar();

    int hits = 0;
    int misses = 0;
    
    for (int i = 0; i < n; i++) {
        int op = acessos[i][0];
        int pg = acessos[i][1];
        acessar_pagina(pg, op, &hits, &misses);
    }

    printf("FIFO -> Hits: %d | Misses: %d\n", hits, misses);

};
/*--FIM FIFO--*/


/*--INICIO NUR--*/
int vitima_nur() {
    int melhor_indice = 0;
    int melhor_classe = INT_MAX;
    int melhor_tempo = INT_MAX;

    for (int i = 0; i < NUM_FRAMES; i++) {
        int pg = frames[i].pagina;
        if (pg == -1) continue;

        int R = tabela_paginas[pg].referenciada;
        int M = tabela_paginas[pg].modificada;

        int classe = (R ? 2 : 0) + (M ? 1 : 0);

        if (classe < melhor_classe || 
           (classe == melhor_classe && tabela_paginas[pg].tempo_carregada < melhor_tempo)) 
        {
            melhor_classe = classe;
            melhor_indice = i;
            melhor_tempo = tabela_paginas[pg].tempo_carregada;
        }
    }

    return melhor_indice;
}

void executar_NUR(int acessos[][2], int n){
    inicializar();

    int hits = 0;
    int misses = 0;

    for (int i = 0; i < n; i++) {
        int op = acessos[i][0];
        int pg = acessos[i][1];

        if (tabela_paginas[pg].presente) {
            hits++;
            tabela_paginas[pg].referenciada = 1;
            if (op) tabela_paginas[pg].modificada = 1;
            tabela_paginas[pg].ultimo_uso = tempo_global++;
        } else {
            misses++;

            int frame = vitima_nur();
            carregar_pagina(frame, pg);

            if (op) tabela_paginas[pg].modificada = 1;
        }
    }

    printf("NUR -> Hits: %d | Misses: %d\n", hits, misses);
}
/*--FIM NUR--*/

/*--INICIO SEGUNDA CHANCE--*/
int vitima_segunda_chance() {
    while (1) {
        int frame = ponteiro_sc;
        int pg = frames[frame].pagina;

        if (tabela_paginas[pg].referenciada == 0) {
            ponteiro_sc = (ponteiro_sc + 1) % NUM_FRAMES;
            return frame;
        } else {
            tabela_paginas[pg].referenciada = 0;
            ponteiro_sc = (ponteiro_sc + 1) % NUM_FRAMES;
        }
    }
}

void executar_SEGUNDA_CHANCE(int acessos[][2], int n){
    inicializar();

    int hits = 0;
    int misses = 0;

    for (int i = 0; i < n; i++) {
        int op = acessos[i][0];
        int pg = acessos[i][1];

        if (tabela_paginas[pg].presente) {
            hits++;
            tabela_paginas[pg].referenciada = 1;
            if (op) tabela_paginas[pg].modificada = 1;
            tabela_paginas[pg].ultimo_uso = tempo_global++;
        } else {
            misses++;

            int frame = vitima_segunda_chance();
            carregar_pagina(frame, pg);

            if (op) tabela_paginas[pg].modificada = 1;
        }
    }

    printf("SEGUNDA_CHANCE -> Hits: %d | Misses: %d\n", hits, misses);
}
/*--FIM SEGUNDA CHANCE--*/

/*-- INICIO CLOCK --*/

int vitima_clock() {
    while (1) {
        int frame = ponteiro_clock;
        int pg = frames[frame].pagina;

        if (tabela_paginas[pg].referenciada == 0) {
            ponteiro_clock = (ponteiro_clock + 1) % NUM_FRAMES;
            return frame;
        } else {
            tabela_paginas[pg].referenciada = 0;
            ponteiro_clock = (ponteiro_clock + 1) % NUM_FRAMES;
        }
    }
}

void executar_CLOCK(int acessos[][2], int n){
    inicializar();

    int hits = 0;
    int misses = 0;

    for (int i = 0; i < n; i++) {
        int op = acessos[i][0];
        int pg = acessos[i][1];

        if (tabela_paginas[pg].presente) {
            hits++;
            tabela_paginas[pg].referenciada = 1;
            if (op) tabela_paginas[pg].modificada = 1;
            tabela_paginas[pg].ultimo_uso = tempo_global++;
        } else {
            misses++;

            int frame = vitima_clock();
            carregar_pagina(frame, pg);

            if (op) tabela_paginas[pg].modificada = 1;
        }
    }

    printf("CLOCK -> Hits: %d | Misses: %d\n", hits, misses);
}

/*-- FIM CLOCK --*/

/*-- Inicio MRU -- */

int vitima_mru() {
    int indice = 0;
    int maior = -1;

    for (int i = 0; i < NUM_FRAMES; i++) {
        int pg = frames[i].pagina;
        if (pg == -1) continue;

        int tempo = tabela_paginas[pg].ultimo_uso;
        if (tempo > maior) {
            maior = tempo;
            indice = i;
        }
    }

    return indice;
}

void executar_MRU(int acessos[][2], int n){
    inicializar();

    int hits = 0;
    int misses = 0;

    for (int i = 0; i < n; i++) {
        int op = acessos[i][0];
        int pg = acessos[i][1];

        if (tabela_paginas[pg].presente) {
            hits++;
            tabela_paginas[pg].referenciada = 1;
            if (op) tabela_paginas[pg].modificada = 1;
            tabela_paginas[pg].ultimo_uso = tempo_global++;
        } else {
            misses++;

            int frame = vitima_mru();
            carregar_pagina(frame, pg);

            if (op) tabela_paginas[pg].modificada = 1;
        }
    }

    printf("MRU -> Hits: %d | Misses: %d\n", hits, misses);
}

/*-Fim MRU--*/


int main(){
    int acessos[][2] = {
        {0,0},{0,1},{1,2},{0,6},{1,7},{1,1},{0,7},{0,6},{0,2},{0,3},
        {1,0},{0,4},{0,0},{1,6},{0,1},{0,8},{0,12},{1,8},{0,2},{0,15},
        {0,6},{1,0},{0,3},{0,5},{0,0}
    };

    int n = sizeof(acessos)/sizeof(acessos[0]);

    executar_FIFO(acessos, n);
    executar_NUR(acessos, n);
    executar_SEGUNDA_CHANCE(acessos, n);
    executar_CLOCK(acessos, n);
    executar_MRU(acessos, n);
}