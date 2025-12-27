import java.util.*;
class Solution {
    public static int[] twoSum(int[] nums, int target) {
        int ar[]=new int[2];
        for(int i=0;i<nums.length;i++){
            for(int j=i+1;j<nums.length;j++){
               int sum=nums[i]+nums[j];
                if(sum==target){
                     ar[0]=i;
                     ar[1]=j;
                     return ar;
                }
            }
        }
       
      
        return ar;
    }
    public static void main(String[] args)
{
    Scanner sc=new Scanner(System.in);


// int []arr=new int[100];
// for(int i=0;i<arr.length;i++){
//     arr[i]=sc.nextInt();
// }
// int tar=sc.nextInt();
// int []rt=twoSum(arr,tar);


}}