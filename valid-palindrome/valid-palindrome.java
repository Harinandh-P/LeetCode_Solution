class Solution {
    public boolean isPalindrome(String s) {
        String S = "";

        for (int i = s.length() - 1; i >= 0; i--) {
            char ch = s.charAt(i);

            if (Character.isLetterOrDigit(ch)) {
                S = S + ch;
            }
        }

        String r = "";

        for (int i = S.length() - 1; i >= 0; i--) {
            char ch = S.charAt(i);
            r = r + ch;
        }

        return S.equalsIgnoreCase(r);
    }
}