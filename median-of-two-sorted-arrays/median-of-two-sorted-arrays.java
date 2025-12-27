import java.util.*;
class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        int n1=nums1.length;
        int n2=nums2.length;
        int [] arr=new int[n1+n2];
        int k=0;
        
        for(int i=0;i<n1;i++){
            arr[k++]=nums1[i];

            
        }
        
        for(int i=0;i<n2;i++){
            arr[k++]=nums2[i];
        }
        Arrays.sort(arr);
        int nu=arr.length;
        if(nu%2==0){
           
            return (arr[(nu/2)-1] + arr[(nu/2)])/2.0;
        }
        else{
            return (arr[(nu/2)]);
        }
    }
}