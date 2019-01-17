package utils;

import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Map;

import util.FileLines;

public class ReadTextUnits {
			
	// to read input already organized into <paraNum \t para>
	public static Map<Integer, String> readParagraph(String file) throws FileNotFoundException{
		Map<Integer, String> paraNum_para = new HashMap<Integer, String>();
		for(String line: new FileLines(file)) {
			int paraNum = Integer.parseInt(line.split("\t")[0]);
			String para = line.split("\t")[1];
			paraNum_para.put(paraNum, para);
		}
		return paraNum_para;
	}

}
