#include <stdio.h>

int main() {
    int n, key, found = 0;
    
    // Read array size
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    
    int arr[n];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    // Read search element
    scanf("%d", &key);
    
    // Linear Search
    for (int i = 0; i < n; i++) {
        if (arr[i] == key) {
            printf("Element %d found at position %d\n", key, i + 1);
            found = 1;
            break;
        }
    }
    
    if (!found) {
        printf("Element %d not found\n", key);
    }
    
    return 0;
}
