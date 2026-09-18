class Solution {
    public String longestCommonPrefix(String[] strs) {
        String rep=strs[0],temp="";
        int i=1,j=0;
        while(i<strs.length){
         for ( int k=0;k<strs[i].length();k++){
            char x=strs[i].charAt(k);
            if ( k<rep.length() && x== rep.charAt(k)){
                 temp+=x;
                j++;
                continue;
            }
            else{
                
                break;
               
            }
         }
         rep=temp;
         temp="";
         i++;
        }
        return rep;
    }
    
}