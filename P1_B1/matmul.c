#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define N 4096   // matrix size (adjust as needed)

// Fill matrix with random doubles
void fill_matrix(double A[N][N]) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            A[i][j] = (double)rand() / RAND_MAX;
}

/* ---------------- six permutations ---------------- */

// ijk
void matmul_ijk(double A[N][N], double B[N][N], double C[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            C[i][j] = 0.0;
            for (int k = 0; k < N; k++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }
}

// jik
void matmul_jik(double A[N][N], double B[N][N], double C[N][N]) {
    for (int j = 0; j < N; j++) {
        for (int i = 0; i < N; i++) {
            C[i][j] = 0.0;
            for (int k = 0; k < N; k++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }
}

// kij
void matmul_kij(double A[N][N], double B[N][N], double C[N][N]) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            C[i][j] = 0.0;

    for (int k = 0; k < N; k++) {
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }
}

// ikj
void matmul_ikj(double A[N][N], double B[N][N], double C[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++)
            C[i][j] = 0.0;

        for (int k = 0; k < N; k++)
            for (int j = 0; j < N; j++)
                C[i][j] += A[i][k] * B[k][j];

    }
}

// jki
void matmul_jki(double A[N][N], double B[N][N], double C[N][N]) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            C[i][j] = 0.0;

    for (int j = 0; j < N; j++) {
        for (int k = 0; k < N; k++) {
            for (int i = 0; i < N; i++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }
}

// kji
void matmul_kji(double A[N][N], double B[N][N], double C[N][N]) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            C[i][j] = 0.0;

    for (int k = 0; k < N; k++) {
        for (int j = 0; j < N; j++) {
            for (int i = 0; i < N; i++)
                C[i][j] += A[i][k] * B[k][j];
        }
    }
}

void matmul_tiled_ijk(double A[N][N], double B[N][N], double C[N][N], int b) {
    for (int i = 0; i < N; i += b)
        for (int j = 0; j < N; j += b)
            for (int k = 0; k < N; k += b)
                for (int ii = i; ii < i + b; ii++)
                    for (int jj = j; jj < j + b; jj++)
                        for (int kk = k; kk < k + b; kk++)
                            A[ii][jj] += B[ii][kk] * C[kk][jj];
}

void matmul_tiled_ikj(double A[N][N], double B[N][N], double C[N][N], int b) {
    for (int i = 0; i < N; i += b)
        for (int k = 0; k < N; k += b)
            for (int j = 0; j < N; j += b)
                for (int ii = i; ii < i + b; ii++)
                    for (int kk = k; kk < k + b; kk++)
                        for (int jj = j; jj < j + b; jj++)
                            A[ii][jj] += B[ii][kk] * C[kk][jj];
}

void matmul_tiled_jik(double A[N][N], double B[N][N], double C[N][N], int b) {
    for (int j = 0; j < N; j += b)
        for (int i = 0; i < N; i += b)
            for (int k = 0; k < N; k += b)
                for (int jj = j; jj < j + b; jj++)
                    for (int ii = i; ii < i + b; ii++)
                        for (int kk = k; kk < k + b; kk++)
                            A[ii][jj] += B[ii][kk] * C[kk][jj];
}

void matmul_tiled_jki(double A[N][N], double B[N][N], double C[N][N], int b) {
    for (int j = 0; j < N; j += b)
        for (int k = 0; k < N; k += b)
            for (int i = 0; i < N; i += b)
                for (int jj = j; jj < j + b; jj++)
                    for (int kk = k; kk < k + b; kk++)
                        for (int ii = i; ii < i + b; ii++)
                            A[ii][jj] += B[ii][kk] * C[kk][jj];
}

void matmul_tiled_kij(double A[N][N], double B[N][N], double C[N][N], int b) {
    for (int k = 0; k < N; k += b)
        for (int i = 0; i < N; i += b)
            for (int j = 0; j < N; j += b)
                for (int kk = k; kk < k + b; kk++)
                    for (int ii = i; ii < i + b; ii++)
                        for (int jj = j; jj < j + b; jj++)
                            A[ii][jj] += B[ii][kk] * C[kk][jj];
}

void matmul_tiled_kji(double A[N][N], double B[N][N], double C[N][N], int b) {
    for (int k = 0; k < N; k += b)
        for (int j = 0; j < N; j += b)
            for (int i = 0; i < N; i += b)
                for (int kk = k; kk < k + b; kk++)
                    for (int jj = j; jj < j + b; jj++)
                        for (int ii = i; ii < i + b; ii++)
                            A[ii][jj] += B[ii][kk] * C[kk][jj];
}


/* -------------------------------------------------- */
int main(int argc, char **argv) {
    static double A[N][N], B[N][N], C[N][N];

    srand(time(NULL));
    fill_matrix(A);
    fill_matrix(B);

    if (argc < 2) {
        printf("Usage: %s <function_name> [block_size]\n", argv[0]);
        return 1;
    }

    char *func = argv[1];
    int b = (argc > 2) ? atoi(argv[2]) : 64;

    if (strcmp(func, "matmul_ijk") == 0) matmul_ijk(A, B, C);
    else if (strcmp(func, "matmul_jik") == 0) matmul_jik(A, B, C);
    else if (strcmp(func, "matmul_kij") == 0) matmul_kij(A, B, C);
    else if (strcmp(func, "matmul_ikj") == 0) matmul_ikj(A, B, C);
    else if (strcmp(func, "matmul_jki") == 0) matmul_jki(A, B, C);
    else if (strcmp(func, "matmul_kji") == 0) matmul_kji(A, B, C);
    else if (strcmp(func, "matmul_tiled_ijk") == 0) matmul_tiled_ijk(A, B, C, b);
    else if (strcmp(func, "matmul_tiled_ikj") == 0) matmul_tiled_ikj(A, B, C, b);
    else if (strcmp(func, "matmul_tiled_jik") == 0) matmul_tiled_jik(A, B, C, b);
    else if (strcmp(func, "matmul_tiled_jki") == 0) matmul_tiled_jki(A, B, C, b);
    else if (strcmp(func, "matmul_tiled_kij") == 0) matmul_tiled_kij(A, B, C, b);
    else if (strcmp(func, "matmul_tiled_kji") == 0) matmul_tiled_kji(A, B, C, b);
    else {
        printf("Unknown function: %s\n", func);
        return 1;
    }

    return 0;
}
