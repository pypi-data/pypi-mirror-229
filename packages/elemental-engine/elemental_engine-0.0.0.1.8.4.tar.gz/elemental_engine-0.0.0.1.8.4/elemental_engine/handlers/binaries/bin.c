#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <wchar.h>
#include <string.h>
#include <math.h>
#include <locale.h>
#include <stdint.h>

#define MAX 1024




int num_zeros;
int str_len; 

void removeChar(char* s, char c)
{
    
    int j, n = strlen(s);
    for (int i = j = 0; i < n; i++)
        if (s[i] != c)
            s[j++] = s[i];
    
    s[j] = '\0';
}

void appendUTF8Character(int8_t codePoint, int8_t *output) {
        output[0] = (int8_t)codePoint;
}

int8_t getUnicodeCodePoint(const char *utf8char) {
    int8_t codePoint;
    const unsigned char *bytes = (const unsigned char *)utf8char;
    
    codePoint = bytes[0];
   
    
    return codePoint;
};

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
        struct Tuple code_generated = validFloat(unicodeCode, &randomIntegerTimes);
    };

    return code_generated;
}

char* zfill(char *str, int width) {
    char *result = (char *) malloc((strlen(str)+1)*sizeof(char));
    
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

// Function to get substr in C
char* getStringLeft(const char *src, int m, int n)
{
    // get the length of the destination string
    int len = n - m;
 
    // allocate (len + 1) chars for destination (+1 for extra null character)
    char *dest = (char*)malloc(sizeof(char) * (len + 1));
 
    // extracts characters between m'th and n'th index from source string
    // and copy them into the destination string
    for (int i = m; i < n && (*(src + i) != '\0'); i++)
    {
        *dest = *(src + i);
        dest++;
    }
 
    // null-terminate the destination string
    *dest = '\0';
    // return the destination string
    return dest - len;
}

int retrieveCode(char *digit) {
    // Extract and convert the parts of the input digit.
    int len = 5;

    char* strMultiplyFactor = getStringLeft(digit, 0, 5);
    int multiplyFactor = atoi(strMultiplyFactor);
    free(strMultiplyFactor);

    char* strPeriodPos = getStringLeft(digit, 10, 15);
    int periodPos = atoi(strPeriodPos);
    free(strPeriodPos);
    
    char* strTempOrdinary = getStringLeft(digit, 15, 20);
    int ordinary = atoi(strTempOrdinary);
    free(strTempOrdinary);

    char strOrdinary[8];
    sprintf(strOrdinary, "%d", ordinary);
    char floatValue[16]; // Assuming a maximum of 32 characters for the float value
    int floatValueIndex = 0;
    for (int index = 0; index < sizeof(ordinary); index++) {
        if (index == periodPos) {
            floatValue[floatValueIndex++] = '.';
        }
        floatValue[floatValueIndex++] = strOrdinary[index];
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

    while (currentDigit != NULL) {

        int result = retrieveCode(currentDigit);

        int8_t currentChar;

        //sscanf(result, "%c", currentChar);
        // Store the result in strResult
        appendUTF8Character((int8_t)result, &currentChar);
        
        strResult[i++] = currentChar;
        
        currentDigit = strtok(NULL, " ,.-");
    }

    strResult[i] = '\0'; // Null-terminate strResult
    free(currentDigit);
    return strResult;
}

    char digit;

    char *utf8char;
    struct Tuple test;

    char decimalPoint = '.';


    int periodPos;

char* encrypt (char *strInput) {
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

        digit = strInput[count];
        utf8char = &digit;
        int8_t unicodeCode = getUnicodeCodePoint(utf8char);
        sprintf(strSeedValue, "%d", unicodeCode);

        srand(unicodeCode);
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

        removeChar(strOrdinary, '.');
        char* zfillMultiplyFactor = zfill(gcvt(test.multiplyFactor, 10, strMultiplyFactor), 5);
        strcat(encryptedValue, zfillMultiplyFactor);
        free(zfillMultiplyFactor);

        char* zfillSeedValue = zfill(strSeedValue, 5);
        strcat(encryptedValue, zfillSeedValue);
        free(zfillSeedValue);

        char* zfillPeriodPos = zfill(strPeriodPos, 5);
        strcat(encryptedValue, zfillPeriodPos);
        free(zfillPeriodPos);

        char* zfillOrdinary = zfill(strOrdinary, 5);
        strcat(encryptedValue, zfillOrdinary);
        free(zfillOrdinary);

        if (strInput[count+1] != '\0') {
            strcat(encryptedValue, " ");
        }

    };
    free(currentChar);
    free(strFloat);
    free(strMultiplyFactor);
    free(strSeedValue);
    free(strPeriodPos);

    return encryptedValue;
}

void freeMemory(char* memory) {
    free(memory);
}

int main () {
    setlocale(LC_ALL, "C");
  char *digit = "abcdefghijklmnopqrstuvwxyz";
  char *encryptedResult = encrypt(digit);
  
  printf("\n%s", encryptedResult);
  char *decryptedResult = decrypt(encryptedResult);

  printf("\nDecrypted Result: %s", decryptedResult);
  freeMemory(encryptedResult);
  return 0;
}
