class Solution {
    public int missingNumber(int[] nums) {
        int n= nums.length;
       int sum=n*(n+1)/2;
       int actSum=0;
       for(int x:nums){
        actSum+=x;
       }
      return sum-actSum;
    }
}