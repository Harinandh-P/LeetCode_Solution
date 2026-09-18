int value(char c) {
    switch (c) {
        case 'I': return 1;
        case 'V': return 5;
        case 'X': return 10;
        case 'L': return 50;
        case 'C': return 100;
        case 'D': return 500;
        case 'M': return 1000;
        default: return 0;
    }
}

int romanToInt(char* s) {
    int ans = 0;
    int num = 0;

    // Find length of string
    int len = 0;
    while (s[len] != '\0')
        len++;

    // Traverse from right to left
    for (int i = len - 1; i >= 0; i--) {
        num = value(s[i]);

        if (4 * num < ans)
            ans -= num;
        else
            ans += num;
    }

    return ans;
}