package utils;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.Map;

import org.deeplearning4j.models.embeddings.wordvectors.WordVectors;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;

import utils.GenericUtils;

public class GetGoogleTags {
	
	public static WordVectors w2v = null;
	
	public static void googleReverseImageSearch(String listImagesFilePath) throws NumberFormatException, IOException{
		
		/*
		 * Reverse image search API deprecated
		 * Google custom search engine does not allow reverse image search
		 * Regular Google reverse image search used to grab google tag suggestions
		 * https://stackoverflow.com/questions/19239811/getting-the-best-guess-info-of-an-image-like-google-reverse-image-search
		 * 
		 * Down-side: limit of 100 queries per IP address
		 */
		
		PrintWriter imagesNoResponse = new PrintWriter(new FileOutputStream(new File("./logs/google/imagesNoResponse.txt"), true));
	
		String writeToFile = "./data/imageTagsGoogle.txt";
		
		Map<String, String> imageName_url = new HashMap<>();
		//TODO populate imageName_url
		
		for(String url: imageName_url.values()){
			String searchUrl = "http://www.google.com/searchbyimage?hl=en&image_url=" + url;
			
			Document doc = Jsoup.connect(searchUrl).userAgent("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36").get();
	
			String response = doc.html();
			
			LinkedList<String> responseLines = new LinkedList<String>();
			
			int targetLineIndex = 0;
			for(String responseLine: response.split("\n")){
				responseLines.add(responseLine);
				if(responseLine.contains("Best guess for this image")) // the line with the suggested image tag is the line after this
					targetLineIndex = responseLines.indexOf(responseLine);
			}
			String imageTagLine = "";
			if(targetLineIndex > 0) // in some cases Google is unable to read the image; for these cases the targetLineIndex remains 0
				imageTagLine = responseLines.get(targetLineIndex+1);
			
			if(imageTagLine.equals("")){
				imagesNoResponse.println(GenericUtils.getKeyFromValue(imageName_url, url));
				imagesNoResponse.flush();
			}
			else{	
				String imageTag = imageTagLine.substring(imageTagLine.lastIndexOf("\">")+2, imageTagLine.lastIndexOf("</"));
				System.out.println(GenericUtils.getKeyFromValue(imageName_url, url) + "\t" + imageTag);
				PrintWriter out = new PrintWriter(new FileOutputStream(new File(writeToFile), true));
				out.println(GenericUtils.getKeyFromValue(imageName_url, url) + "\t" + imageTag);
				out.flush();
				out.close();
			}
		}
		
		imagesNoResponse.close();
	}
}
