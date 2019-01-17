package utils;

import java.io.File;
import java.io.UnsupportedEncodingException;

public class ResolveUrlEncoding {
	
	public static String findCorrespondingImageName(String image, String folder) throws UnsupportedEncodingException{
		/*
		 * downloaded image names can be URL encoded and result in mismatch
		 */
		
		String correspondingGTimageName = "";
		
		if(image.contains("%")) {
			correspondingGTimageName = java.net.URLDecoder.decode(image, "UTF-8");
		}
		else {
			correspondingGTimageName = java.net.URLEncoder.encode(image, "UTF-8");	
		}
		//TODO: check this
		if(new File(folder + "/" + correspondingGTimageName).exists()) {
			return correspondingGTimageName;
		}
		else {
			return null;
		}
	}
}
