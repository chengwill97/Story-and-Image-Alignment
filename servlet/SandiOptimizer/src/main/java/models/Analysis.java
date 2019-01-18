package models;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import evaluation.SemanticAccuracy;
import models.ILPBased;
import utils.GenericUtils;

public class Analysis {

	public Map<String, Map<Integer, Double>> sim_allImagesParas(
			Map<Integer, String> alignedParaNum_imageName, 
			Map<String, Set<String>> imageName_tags,
			Map<Integer, List<String>> para_distinctiveConcepts){
		
		Map<String, Map<Integer, Double>> image_para_cosine = new HashMap<>();
		
		for(String image: alignedParaNum_imageName.values()){
			List<String> tags = new ArrayList<>();
			tags.addAll(imageName_tags.get(image));
			Map<Integer, Double> para_cosine = new HashMap<>();
	
			for(int paraNum: para_distinctiveConcepts.keySet()){
				List<String> paraConcepts = para_distinctiveConcepts.get(paraNum);
				double semSim = 0.0;
				try {
					semSim = SemanticAccuracy.semanticSimilarity(tags, paraConcepts, ILPBased.w2v);
				} catch (IOException e) {
					e.printStackTrace();
				}
				para_cosine.put(paraNum, semSim);
			}
			image_para_cosine.put(image, para_cosine);
		}
		
		return image_para_cosine;
	}

	public Map<String, List<String>> sim_imageAlignedPara(
			Map<Integer, String> alignedParaNum_imageName, 
			Map<String, Set<String>> imageName_tags,
			Map<Integer, List<String>> para_distinctiveConcepts) throws IOException{
	
		Map<String, List<String>> image_topkParaConcepts = new HashMap<>();
		
		for(String image: alignedParaNum_imageName.values()){
			List<String> tags = new ArrayList<>();
			tags.addAll(imageName_tags.get(image));
			int paraNum = (int) GenericUtils.getKeyFromValue(alignedParaNum_imageName, image);
			List<String> paraConcepts = para_distinctiveConcepts.get(paraNum);
			
			Map<String, Double> paraConcept_cosine = new HashMap<>();
			for(String concept: paraConcepts){
				if(ILPBased.w2v.hasWord(concept)){
					List<String> singleConcept = new ArrayList<>();
					double semSim = 0.0;
					singleConcept.add(concept);
					try {
						semSim = SemanticAccuracy.semanticSimilarity(tags, singleConcept, ILPBased.w2v);
					} catch (IOException e) {
						e.printStackTrace();
					}
					paraConcept_cosine.put(concept, semSim);
				}
			}
			List<String> topkParaConcepts = new ArrayList<>();
			topkParaConcepts.addAll(GenericUtils.getTopNbyValue(GenericUtils.sortByValue(paraConcept_cosine), 5).keySet());
			
			image_topkParaConcepts.put(image, topkParaConcepts);
		}
		
		return image_topkParaConcepts;
	}
}