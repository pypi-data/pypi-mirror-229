#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <wchar.h>
#include <string.h>
#include <math.h>
#include <locale.h>
#include <stdint.h>

#define MAX 4096

struct Tuple {
    float floatValue;
    int randomIntegerTimes;
    int multiplyFactor;
};

struct Tuple validFloat (char unicodeCode, int *randomIntegerTimes) {
    (*randomIntegerTimes)++;
    int multiplyFactor = rand() % (2 -49);
    float floatValue = ceilf((roundf((floorf(((float)unicodeCode / multiplyFactor) * 100) / 100) * 100) / 100)* 100)/100;
    int floatMaxLength = 5;
    int floatActualLength = strlen((char[]){floatValue});
    if (floatActualLength > floatMaxLength) {
        struct Tuple result = {-1.0, 0, 0};
        return result;
    } else {
        struct Tuple result = {floatValue, *randomIntegerTimes, multiplyFactor};
        return result;
    }
}

struct Tuple generateCode(char digit, char unicodeCode) {
    int randomIntegerTimes = 0;

    struct Tuple code_generated = validFloat(unicodeCode, &randomIntegerTimes);
    while (code_generated.floatValue <= 0.0) {
        code_generated = validFloat(unicodeCode, &randomIntegerTimes);
    };

    return code_generated;
}

char* zfill(char *str, int width) {
    char *result = (char *) malloc((strlen(str)+1)*sizeof(char));

    int num_zeros;
    int str_len;

    str_len = strlen(str);
    // Calculate the number of zeros to prepend.
    num_zeros = width - str_len;

    // Fill the leftmost part of the result with zeros.
    for(int i = 0; i < num_zeros; i++) {
        result[i] = '0';
    }

    // Copy the original string after the zeros.
    for(int i = num_zeros; i < width; i++) {
        result[i] = str[i - num_zeros];
    }

    // Null-terminate the result.
    result[width+1] = '\0';

    return result;
}

char* getStringLeft(const char *src, int m, int n) {
    // Calculate the length of the substring
    int len = n - m;

    // Check if the requested substring is valid
    if (len <= 0 || m < 0 || n < m)
        return NULL;

    // Allocate memory for the destination string (+1 for the null terminator)
    char *dest = (char*)malloc(sizeof(char) * (len + 1));

    // Check if memory allocation failed
    if (dest == NULL)
        return NULL;

    // Copy characters from source to destination
    for (int i = 0; i < len; i++) {
        dest[i] = src[m + i];

        // Null-terminate the destination string
        if (src[m + i] == '\0') {
            dest[i + 1] = '\0';
            break;
        }
    }

    return dest;
}

int retrieveCode(char *digit) {
    int stringAllocationSize = 5;
    char* strMultiplyFactor = getStringLeft(digit, 0, 5);
    int multiplyFactor = atoi(strMultiplyFactor);

    char* strPeriodPos = getStringLeft(digit, 10, 15);
    int periodPos = atoi(strPeriodPos);

    char* strTempOrdinary = getStringLeft(digit, 15, 20);
    int ordinary = atoi(strTempOrdinary);

    char tempOrdinary[8];
    sprintf(tempOrdinary, "%d", ordinary);
    char floatValue[16];

    int floatValueIndex = 0;
    int ordinaryLength = sizeof(ordinary);
    for (int index = 0; index < ordinaryLength; index++) {
        if (index == periodPos) {
            floatValue[floatValueIndex++] = '.';
        }
        floatValue[floatValueIndex++] = tempOrdinary[index];
    }

    floatValue[floatValueIndex] = '\0';
    
    float result = atof(floatValue) * multiplyFactor;

    return (int)roundf(result);
    }

char* decrypt(char *strInput) {
    int i = 0;
    char *strResult = (char *)malloc(strlen(strInput) * sizeof(char)); // Allocate memory for strResult

    char *currentDigit;
    currentDigit = strtok(strInput, " ");

    int decryptDigit;

    while (currentDigit != NULL) {

        int result = retrieveCode(currentDigit);

        decryptDigit = (int)result;
        
        strResult[i++] = decryptDigit;
        
        currentDigit = strtok(NULL, " ,.-");
    }

    strResult[i] = '\0'; // Null-terminate strResult

    return strResult;

}

char* encrypt (char *strInput) {
    int periodPos;
    char decimalPoint = '.';
    int totalLength = 0; // Initialize the total length
    int partLength = MAX;
    for (int count = 0; strInput[count] != '\0'; count++) {
        // Calculate the length of each part and add it to the total length
         // Adjust as needed
        totalLength += partLength;

        if (strInput[count+1] != '\0') {
            totalLength += 1; // Add space length
        }
    }  

    char *currentChar = (char *) malloc(16);
    char *strFloat = (char *) malloc(16);
    char *strOrdinary = (char *) malloc(16);
    char *strMultiplyFactor = (char *) malloc(16);
    char *strSeedValue = (char *) malloc(16);
    char *strPeriodPos = (char *) malloc(16);
    char *encryptedValue = (char *)malloc(MAX);

    if (encryptedValue == NULL) {
        printf("Error: Failed to allocate encrypted");
        encryptedValue[0] = '\0';
    }

    for(int count = 0; strInput[count] != '\0'; count++) {
        char digit;
        digit = strInput[count];
        char *utf8char;
        utf8char = &digit;

        int unicodeCode =  (const unsigned char)utf8char[0];
        sprintf(strSeedValue, "%d", unicodeCode);

        srand(unicodeCode);
        struct Tuple test;
        test = generateCode(digit, unicodeCode);
        sprintf(strFloat, "%.2f", test.floatValue);

        for (int i = 0; i <= strlen(strFloat); i++) {
            if (strFloat[i] == decimalPoint) {
                periodPos = i;
                sprintf(strPeriodPos, "%d", periodPos);
                break;
            }
        }

        strOrdinary = strFloat;

        int j, n = strlen(strOrdinary);
        for (int i = j = 0; i < n; i++)
            if (strOrdinary[i] != '.')
                strOrdinary[j++] = strOrdinary[i];
            strOrdinary[j] = '\0';


        char* multiplyFactorTemp = gcvt(test.multiplyFactor, 10, strMultiplyFactor);
        char* zfillMultiplyFactor = zfill(multiplyFactorTemp, 5);
        strcat(encryptedValue, zfillMultiplyFactor);
        //free(zfillMultiplyFactor);

        char* zfillSeedValue = zfill(strSeedValue, 5);
        strcat(encryptedValue, zfillSeedValue);
        //free(zfillSeedValue);

        char* zfillPeriodPos = zfill(strPeriodPos, 5);
        strcat(encryptedValue, zfillPeriodPos);
        //free(zfillPeriodPos);

        char* zfillOrdinary = zfill(strOrdinary, 5);
        strcat(encryptedValue, zfillOrdinary);
        //free(zfillOrdinary);

        if (strInput[count+1] != '\0') {
            strcat(encryptedValue, " ");
        }

    };
    //free(currentChar);
    //free(strFloat);
    //free(strMultiplyFactor);
    //free(strSeedValue);
    //free(strPeriodPos);

    return encryptedValue;

}



int main () {
  char *digit = "abc";
  for(int i = 0; i < 10; i++) {
    char *encryptedResult = encrypt(digit);
  char *decryptedResult = decrypt(encryptedResult);
  printf("\nResult: \n\t Encrypted: %s, \n\t Decrypted: %s", encryptedResult, decryptedResult);
  }
  return 0;
}
