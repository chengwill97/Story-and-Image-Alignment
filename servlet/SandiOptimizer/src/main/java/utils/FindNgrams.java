package utils;

import java.util.ArrayList;
import java.util.List;

public class FindNgrams {
	
	public static List<String> ngrams(int n, String str) {
        List<String> ngrams = new ArrayList<String>();
        String[] words = str.split(" ");
           
        for (int i = 0; i < words.length - n + 1; i++)
            ngrams.add(concat(words, i, i+n));
        
        return ngrams;
    }

    public static String concat(String[] words, int start, int end) {
        StringBuilder sb = new StringBuilder();
        for (int i = start; i < end; i++){
        	//System.out.println("Looking at.................." + words[i]);
        	if(words[i].trim().length() > 0){
        		sb.append((i > start ? "_" : "") + words[i].trim());
        	}
        }
        return sb.toString();
    }

}
