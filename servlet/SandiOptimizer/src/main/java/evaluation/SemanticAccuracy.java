package evaluation;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.deeplearning4j.models.embeddings.wordvectors.WordVectors;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.ops.transforms.Transforms;


public class SemanticAccuracy {
	
	public static double semanticSimilarity(String originalPara, String alignedPara, WordVectors w2v) throws IOException {
		Set<String> stopWords = new HashSet<String>(Files.readAllLines(Paths.get("./resources/NLTK_CoreNLP_englishStopWords.txt")));
		Set<String> para1Concepts = new HashSet<>(Arrays.asList(originalPara.replaceAll("\\p{P}", "").split(" "))); // replace punctuation before splitting into words
		para1Concepts.removeAll(stopWords);
				
		Set<String> para2Concepts = new HashSet<>(Arrays.asList(alignedPara.replaceAll("\\p{P}", "").split(" "))); // replace punctuation before splitting into words
		para2Concepts.removeAll(stopWords);
		
		//-----------------------------------------------------------------------------
		/*
		 * W2V pre-trained model would contain some out of vocabulary words.
		 * This renders the entire mean vector null
		 * We remove those out of vocabulary words from the list of distinctive words
		 */
		List<String> paraWordsOrig_removeList = new ArrayList<String>();
		List<String> paraWordsAligned_removeList = new ArrayList<String>();
		
		try{
			for(String word: para1Concepts){
				//System.out.println(word);
				if(!w2v.vocab().containsWord(word))
					paraWordsOrig_removeList.add(word);
			}
			for(String word: para2Concepts){
				if(!w2v.vocab().containsWord(word))
					paraWordsAligned_removeList.add(word);
			}
		}catch(Exception e){
			System.out.println("Error " + e + "wierd!!!");
		}
		if(paraWordsOrig_removeList.isEmpty() || paraWordsOrig_removeList == null)
			para1Concepts.removeAll(paraWordsOrig_removeList);
		if(paraWordsAligned_removeList.isEmpty() || paraWordsAligned_removeList == null)
			para2Concepts.removeAll(paraWordsAligned_removeList);
		//-------------------------------------------------------------------------------
		
		double srel = 0.0;
		try{
			INDArray wordVecParaOrig = w2v.getWordVectorsMean(para1Concepts);
			INDArray wordVecParaAligned = w2v.getWordVectorsMean(para2Concepts); // vector representation for the entire paragraph: para2vec
			srel = Transforms.cosineSim(wordVecParaOrig, wordVecParaAligned);
		}catch(Exception e){
			System.out.println("Error " + e + "w2v doesn't contain the word perhaps?");
		}
		return srel;
	}
	
	
	public static double semanticSimilarity(List<String> para1, List<String> para2, WordVectors w2v) throws IOException {
		
		if(para1 == null || para1.isEmpty() || para2.isEmpty() || para2 == null)
			return 0.0;

		//----------------------------------------------------------------------------------------------------------------------------------
		/*
		 * W2V pre-trained model would contain some out of vocabulary bigrams
		 * This renders the entire mean vector null
		 * We remove those out of vocab bigrams from the list of distinctive concepts
		 * and add the unigrams when it is present in w2v
		 */
		List<String> para1_removeList = new ArrayList<String>();
		List<String> para2_removeList = new ArrayList<String>();
		
		List<String> para1_addList = new ArrayList<String>();
		List<String> para2_addList = new ArrayList<String>();
		
		try{
			for(String bigram: para1){
				if(!w2v.vocab().containsWord(bigram)){
					para1_removeList.add(bigram);
					String[] words = bigram.split("_");
					for(String word: words){
						if(w2v.vocab().containsWord(word))
							para1_addList.add(word);
					}
				}
			}
			for(String bigram: para2){
				if(!w2v.vocab().containsWord(bigram)){
					para2_removeList.add(bigram);
					String[] words = bigram.split("_");
					for(String word: words){
						if(w2v.vocab().containsWord(word))
							para2_addList.add(word);
					}
				}
			}
		}catch(Exception e){
			System.out.println("Error " + e + "wierd!!!");
		}
		
		if(!para1_removeList.isEmpty() || para1_removeList != null)
			para1.removeAll(para1_removeList);
		if(!para2_removeList.isEmpty() || para2_removeList != null)
			para2.removeAll(para2_removeList);
		
		if(!para1_addList.isEmpty() || para1_addList != null)
			para1.addAll(para1_addList);
		if(!para2_addList.isEmpty() || para2_addList != null)
			para2.addAll(para2_addList);
		//----------------------------------------------------------------------------------------------------------------------------------
		
		double srel = 0.0;
		if(para1.size() < 1 || para2.size() < 1)
			return 0.0;
			
		INDArray meanPara1 = w2v.getWordVectorsMean(para1);
		INDArray meanPara2 = w2v.getWordVectorsMean(para2);
		srel = Transforms.cosineSim(meanPara1, meanPara2);
		
		// to avoid overflow error(?); for e.g. 1.00000000000002
		if(srel > 1){
			srel = 1.0;
		}
		
		return srel;
	}

}
