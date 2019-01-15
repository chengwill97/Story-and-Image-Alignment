package models;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.deeplearning4j.models.embeddings.loader.WordVectorSerializer;
import org.deeplearning4j.models.embeddings.wordvectors.WordVectors;

import gurobi.GRB;
import gurobi.GRBConstr;
import gurobi.GRBEnv;
import gurobi.GRBException;
import gurobi.GRBLinExpr;
import gurobi.GRBModel;
import gurobi.GRBVar;
import evaluation.SemanticAccuracy;
import utils.ExtractPhrases;
import utils.GenericUtils;

public class ILPBased {
	
	public static WordVectors w2v = null;
	public static Set<String> stopWords = new HashSet<>();
	public static ExtractPhrases phrases = null;
	public static ILPBased ilp = null;
	public static ModelUtils modelUtils = null;
	
	public ILPBased(String pathToW2V) throws IOException{
		
		System.out.println("Loading vectors....patience!!"); // takes up a lot of memory
		
		// load word vectors
//		File googleModel = new File(pathToW2V);
//		w2v = WordVectorSerializer.loadGoogleModel(googleModel, true);
		
		//use image description model
		File gloveModel = new File(pathToW2V);
		w2v = WordVectorSerializer.readWord2VecModel(gloveModel);
		
		System.out.println("Done loading vectors!");		
	}
	
	public static void align(Map<String, Set<String>> imageName_tags, Map<Integer, List<String>> para_distinctiveConcepts, int numImages, String input_folder) throws GRBException, FileNotFoundException{
		
		PrintWriter out = new PrintWriter(new FileOutputStream(new File(input_folder + "/alignments.txt")));

		/*
		 * number of images are specific to each article, and can come from
		 * - user input
		 * - number of images for which we have tags
		 */

		int numParas = para_distinctiveConcepts.size();
		
		//System.out.println("Num of images: " + numImages);
		//System.out.println("Num of paras: " + numParas);
		
		try{
			//-------------------------------------------------------------------------------------------------------------------
			GRBEnv env = new GRBEnv("./gurobiLogs/sandi-demo.log");
			GRBModel model = new GRBModel(env);
			model.reset();
		
			GRBLinExpr expr = new GRBLinExpr();
			GRBVar[][] X = new GRBVar[numImages][numParas];
			
			//-------------------------------------------------------------------------------------------------------------------
			
			// index images
			Map<String, Integer> imageName_index = new HashMap<>();
			int i = 1;
			for(String imageName: imageName_tags.keySet()){
				imageName_index.put(imageName, i);
				i++;
			}
			// TODO: case where images don't have tags
			
			// create variables
			double srel_it = 0.0;
			
			for(String imageName: imageName_tags.keySet()){
				int imageIndex = imageName_index.get(imageName);
				for(int paraNum: para_distinctiveConcepts.keySet()){
					//System.out.println("\n" + (imageIndex-1) + "\t" + (paraNum-1));
					X[imageIndex-1][paraNum-1] = model.addVar(0.0, 0.0, 0.0, GRB.BINARY, "x_"+ String.valueOf(imageIndex) + "_" + String.valueOf(paraNum));
				}
			}
			
			// add variables
			for(String imageName: imageName_tags.keySet()){
				Set<String> origTags = imageName_tags.get(imageName);
				List<String> tags = new ArrayList<String>();
				if(origTags.isEmpty() || origTags == null){
					// no predictions; skip image
					continue;
				}
				//-------------------------------------------------------------------------------------------------------------				

				/*
				 * using bigrams
				 * w2v pre-trained models contain some phrases
				 * replace space in tag by underscore
				 * also replace hyphen by underscore since w2v doesn't contain hyphenated words
				 */
				for(String tag: origTags){
					tags.add(tag.replace(" ", "_").replace("-", "_"));
				}
				
				if(tags.isEmpty() || tags == null)
					continue;
				//-------------------------------------------------------------------------------------------------------------

				int imageIndex = imageName_index.get(imageName);
				tags.add("a"); // adding a word to avoid error for getWordVectorMean - this method needs at least one word
				
				for(int paraNum: para_distinctiveConcepts.keySet()){
					List<String> paraWords = new ArrayList<String>(para_distinctiveConcepts.get(paraNum)); // can be unigrams or bigrams
					try{
						srel_it = SemanticAccuracy.semanticSimilarity(tags, paraWords, w2v);
					}catch(Exception e){
						System.out.println("Error " + e + "...para " + paraNum + " contains 0 words");
					}
					
					// make GRB expression					
					X[imageIndex-1][paraNum-1] = model.addVar(0.0, 1.0, srel_it, GRB.BINARY, "x_"+ String.valueOf(imageIndex) + "_" + String.valueOf(paraNum));
					expr.addTerm(srel_it, X[imageIndex-1][paraNum-1]);
				}
			}
			model.update();
			//------------------------------------------------------------------------------------------------------------------

			// set objective function
			model.setObjective(expr, GRB.MAXIMIZE); //expr was created while creating the variables
			model.update();
			
			// Add constraints
			List<GRBConstr> X_constr_row = new ArrayList<>();
			List<GRBConstr> X_constr_column = new ArrayList<>();
			
			/* Add constraint: for each image i, sum_t X_it <=1; t = 1:number of paragraphs
			 * each image can appear only once in the article. This is a trivial assumption - regular blog posts do not contain the same image multiple times
			 */
			for(int img = 1; img <= numImages; img ++){
				expr = new GRBLinExpr();
				for(int t = 1; t <= numParas; t ++){
					expr.addTerm(1, X[img-1][t-1]);
				}
				try{
					GRBConstr c = model.addConstr(expr, GRB.LESS_EQUAL, 1.0, "c_x" +"_row" + String.valueOf(img));
					X_constr_row.add(c);
				}catch(Exception e){
					System.out.println("Exception " + e.getMessage() + " for article size of GRB variable " + X.length);
					continue;
				}
			}
			/* Add constraint: for each text unit t, sum_i X_it <=1; i = 1:number of images
			 * each paragraph can be associated with at most one image
			 */
			for(int t = 1; t <= numParas; t++){
				expr = new GRBLinExpr();
				for(int img = 1; img <= numImages; img ++){
					expr.addTerm(1, X[img-1][t-1]);
				}
				try{
					GRBConstr c = model.addConstr(expr, GRB.LESS_EQUAL, 1.0, "c_x" +"_column" + String.valueOf(t));
					X_constr_column.add(c);
				}catch(Exception e){
					System.out.println("Exception " + e.getMessage() + " for article size of GRB variable " + X.length);
					continue;
				}
			}
			
			// selection constraint
			expr = new GRBLinExpr();
			for(int t = 1; t <= numParas; t++){				
				for(int img = 1; img <= numImages; img ++){
					expr.addTerm(1, X[img-1][t-1]);
				}
			}
			try {
				GRBConstr c = model.addConstr(expr, GRB.LESS_EQUAL, numImages, "selection");
				X_constr_column.add(c);
			}catch(Exception e) {
				
			}
			
			model.update();
			
			//------------------------------------------------------------------------------------------------------------------
		    
			// Optimize model
		    model.set(GRB.DoubleParam.TimeLimit, 600);
		    model.getEnv().set(GRB.IntParam.OutputFlag, 0);
			model.optimize();
			//------------------------------------------------------------------------------------------------------------------
			
			// process results
			for(int img = 1; img <= numImages; img ++){
				for(int t = 1; t <= numParas; t ++){
					String varName = X[img-1][t-1].get(GRB.StringAttr.VarName);
					int imageIndex = Integer.parseInt(varName.split("_")[1]);
					String imageName = GenericUtils.getKeyFromValue(imageName_index, imageIndex).toString();
					int paraNum = Integer.parseInt(varName.split("_")[2]);
					if(X[img-1][t-1].get(GRB.DoubleAttr.X) == 1.0){
						out.println(paraNum + "\t" + imageName);
						out.flush();
					}
				}
			}
			
		}catch(GRBException e){
			System.out.println("Error code: " + e.getErrorCode() + ". " + e.getMessage());
		}
	}
	
//	public static void main(String[] args) throws GRBException, IOException {
//		/*
//		 *  input to the jar file: input_folder
//		 *  e.g. java -jar align.jar input_folder num_images
//		 */
//		
//		String input_folder = args[0];
//		int numImages = Integer.parseInt(args[1]);
//		String pathToW2V = args[2];
//		
//		// solve an ILP for alignment
//		ilp = new ILPBased(pathToW2V);
//		
//		ExtractPhrases phrases = new ExtractPhrases();
//		
//		String articleText = input_folder + "/paragraph.txt";
//		
//		Map<Integer, List<String>> para_distinctiveConcepts = phrases.distinctivePhrasesPerParagraph(articleText);
//		
//		Map<String, Set<String>> imageName_tags = new HashMap<>();
//		imageName_tags = ModelUtils.readImageTags(input_folder);
//		
//		//int numParas = para_distinctiveConcepts.keySet().size();
//		
//		
//		/*if(numImages == 0) {
//			if(imageName_tags.size() < numParas) {
//				numImages = imageName_tags.size();	// TODO: if user enters the number of images this gets overwritten
//			}
//			else {
//				numImages = numParas;
//			}
//		}*/
//		
//		System.out.println("Alignments in progress...");
//		align(imageName_tags, para_distinctiveConcepts, numImages, input_folder);
//		
//	}
}
