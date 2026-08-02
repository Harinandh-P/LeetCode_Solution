class Solution {
    public int findDuplicate(int[] nums) {
     Arrays.sort(nums);
     int i=0,dup=0;
     while(true){
        if(nums[i]==nums[i+1]){
            dup=nums[i];
            break;
        }
        i++;
     }
      return dup;  
    }
}