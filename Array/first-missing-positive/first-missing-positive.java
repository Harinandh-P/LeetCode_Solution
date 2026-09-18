class Solution {
    public int firstMissingPositive(int[] nums) {
        Arrays.sort(nums);
        int min=1;
        for (int x:nums){
            if(min== x){
               min++;
               
            }
        }
        return min;
    }
}