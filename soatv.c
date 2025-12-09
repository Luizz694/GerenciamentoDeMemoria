#include <stdio.h>
#include <stdlib.h>

#define NUMPAGVIRTUAL 16
#define NUMPAGFISICA 8

typedef struct {
    int presente;
    int referenciada;
    int moldura;
    int modificada;
} Pagina;

Pagina Memoria_virtual[NUMPAGVIRTUAL];
int Memoria_fisica[NUMPAGFISICA];

//dados de entrada
typedef struct {
    char aux;
    int alvo;
} Teste;

/*
implementar os algoritmos 
1. Não usada recentemente (NUR);
2. Primeira a entrar, primeira a sair;
3. Segunda chance (SC);
4. Relógio;
5. Menos recentemente usada (MRU)
*/

void fifo(){
    int hit = 0, miss = 0;
    int fila[NUMPAGFISICA];
    int inicio_fila = 0;
    int fim_fila = 0;

    int acessos = 25;

    char operacoes[] = {'R', 'R', 'M', 'R', 'M', 'M', 'R', 'R', 'R', 'R',
                        'M', 'R', 'R', 'M', 'R', 'R', 'R', 'M', 'R', 'R',
                        'R', 'M', 'R', 'R', 'R'};
    int paginas[] = {0, 1, 2, 6, 7, 1, 7, 6, 2, 3,
                     0, 4, 0, 6, 1, 8, 12, 8, 2, 15,
                     6, 0, 3, 5, 0};
    

    for (int i = 0; i < NUMPAGFISICA; i++){
        if (Memoria_fisica[i] =! -1){
             fila[fim_fila++] = Memoria_fisica[i];
        }
    }

    for (int i = 0; i < acessos; i++){
        char op = operacoes[i];
        char aux = paginas[i];
    
    }
    
    
}

int main() {
    // A sequencia completa de acessos
    return 0;
}



