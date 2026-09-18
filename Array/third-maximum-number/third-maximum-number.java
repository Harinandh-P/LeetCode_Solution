class Solution {
    public int thirdMax(int[] nums) {
         Set <Integer> thirdmax= new TreeSet<>();
         int max=0;
         for(int i=0;i<nums.length;i++){
            thirdmax.add(nums[i]);
         }
         List <Integer> fin=new ArrayList<>();
         for(int x:thirdmax){
            fin.add(x);
         }
         if(fin.size()>2){
            max=fin.get(fin.size()-3);
         }
         else{
            max=fin.get(fin.size()-1);
         }
        return max;
    }
}