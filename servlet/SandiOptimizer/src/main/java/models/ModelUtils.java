package models;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.UnsupportedEncodingException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import util.FileLines;

public class ModelUtils{
	
	public static Set<String> imageNames = new HashSet<>(); // set of images for the article
	
	public static Map<String, Set<String>> readImageTags(String input_folder) throws FileNotFoundException, UnsupportedEncodingException {
		/*
		 *  read all image tags into a set
		 *  image tags include: objects, scenes, CSK concepts
		 */
		imageNames.clear();
		Map<String, Set<String>> imgTags = new HashMap<>(); // set of all image tags for each image in the article
	
		for(File file: new File(input_folder + "/images/").listFiles()){
			if(!file.getName().contains(".jpg")) {
				if(!file.getName().contains(".png"))
					continue;
			}
			if(file.getName().contains(".jpg"))
				imageNames.add(file.getName().substring(0, file.getName().lastIndexOf(".jpg")));
			if(file.getName().contains(".png"))
				imageNames.add(file.getName().substring(0, file.getName().lastIndexOf(".png")));
		}
		if(imageNames.isEmpty()){
			return imgTags;
		}
		
		// tags.txt file contains tags from YOLO, scene detection, and Google (?)
		/*
		 * TODO: for Google check if English, get bigram
		 */
		for(String line: new FileLines(input_folder + "/tags.txt")) {
			String imageName = line.split("\t")[0];
			Set<String> tags = new HashSet<String>(Arrays.asList(line.split("\t")[1].split(", ")));
			imgTags.put(imageName, tags);
		}
		
		return imgTags;
	}
}
