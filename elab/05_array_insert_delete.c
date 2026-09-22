#include <stdio.h>

int main() {
    int n, pos, val, del_pos;
    if (scanf("%d", &n) != 1 || n <= 0) return 0;
    
    int arr[100];
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    // Read position and value to insert (1-based index)
    scanf("%d %d", &pos, &val);
    
    // Insertion
    if (pos >= 1 && pos <= n + 1) {
        for (int i = n; i >= pos; i--) {
            arr[i] = arr[i - 1];
        }
        arr[pos - 1] = val;
        n++;
    }
    
    // Print after insertion
    for (int i = 0; i < n; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
    
    // Read position to delete (1-based index)
    if (scanf("%d", &del_pos) == 1) {
        if (del_pos >= 1 && del_pos <= n) {
            for (int i = del_pos - 1; i < n - 1; i++) {
                arr[i] = arr[i + 1];
            }
            n--;
        }
        
        // Print after deletion
        for (int i = 0; i < n; i++) {
            printf("%d ", arr[i]);
        }
        printf("\n");
    }
    
    return 0;
}
