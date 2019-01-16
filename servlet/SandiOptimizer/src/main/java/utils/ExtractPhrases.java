package utils;

import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import util.FileLines;

public class ExtractPhrases {

	public static MaxentTagger tagger = new MaxentTagger(); // Standford POS Tagger requirement
	public static String next="";
	
	public ExtractPhrases(String postagger) {
		
		tagger = new MaxentTagger(postagger);
	}
	
	public static Set<String> returnNounPhrases(String text){
		String taggedText = tagger.tagString(text);
		Set<String> noun_phrases = new HashSet<String>();
		
		if (taggedText == null)
			return noun_phrases;
		
		String[] tokens = taggedText.split("\\s+");
		String phrase="";
		
		//extract noun phrases
		for(int i=0; i<tokens.length; i++){
			String current=tokens[i];
			if(current.substring(0, current.lastIndexOf('_')).length()<2)
				continue;
						
			if(current.substring(current.lastIndexOf('_')+1).equals("NN")
			|| current.substring(current.lastIndexOf('_')+1).equals("NNS")
			|| current.substring(current.lastIndexOf('_')+1).equals("NNPS")
			|| current.substring(current.lastIndexOf('_')+1).equals("JJ")
			|| current.substring(current.lastIndexOf('_')+1).equals("JJS")){
				next="";
				if((i+1)<tokens.length)
					next = tokens[i+1];
				if(next.substring(next.lastIndexOf('_')+1).equals("NN")
				|| next.substring(next.lastIndexOf('_')+1).equals("NNS")
				|| next.substring(next.lastIndexOf('_')+1).equals("NNPS")){
					i++;
					phrase=(current.split("_")[0] + " " + next.split("_")[0]).replaceAll("[^\\w\\s]",""); //the replace removes all wierd characters
					if(!noun_phrases.contains(phrase) && phrase.length() > 2)
							noun_phrases.add(phrase.trim());
				}
				
				// adding this part to consider single nouns and adjectives
				else {
					if(!noun_phrases.contains(current.split("_")[0]) && current.split("_")[0].length() > 2)
						noun_phrases.add(current.split("_")[0].replaceAll("[^\\w\\s]","").trim());
				}
					
			}
			else if(current.substring(current.lastIndexOf('_')+1).equals("NNP")){
				if((i+1)<tokens.length)
					next = tokens[i+1];
				if(next.substring(next.lastIndexOf('_')+1).equals("NNP")){
					i++;
					phrase=(current.split("_")[0] + " " + next.split("_")[0]).replaceAll("[^\\w\\s]","");
					if(!noun_phrases.contains(phrase) && phrase.length() > 2)
						noun_phrases.add(phrase.trim());
				}
				else
					if(!noun_phrases.contains(current.split("_")[0]) && current.split("_")[0].length() > 2)
						noun_phrases.add(current.split("_")[0].replaceAll("[^\\w\\s]","").trim());
			}
		}
		
		noun_phrases.add("a");
		
		if(noun_phrases.size() >= 1)
			return noun_phrases;
		else
			return null;
	}
	
	public Map<Integer, List<String>> distinctivePhrasesPerParagraph(String paragraphs) throws FileNotFoundException {
		
		Map<Integer, List<String>> para_distinctivePhrases = new HashMap<>();
		
		for(String line: new FileLines(paragraphs)) {
			int paraNum = Integer.parseInt(line.split("\t")[0]);
			String para = line.split("\t")[1];
			
//			System.out.println(returnNounPhrases(para));
			
			List<String> phrases = new ArrayList<String>(returnNounPhrases(para));
			para_distinctivePhrases.put(paraNum, phrases);
		}
		
		return para_distinctivePhrases;
	}

}
