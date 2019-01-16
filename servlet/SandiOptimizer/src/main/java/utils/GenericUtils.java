package utils;

import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

public class GenericUtils {

	/*
	 * basic functions on Maps
	 */
	
	public static <K, V extends Comparable<? super V>> Map<K, V> sortByValue(Map<K, V> map) {
	    return map.entrySet()
	              .stream()
	              .sorted(Map.Entry.comparingByValue(Collections.reverseOrder())) // sort in descending order
	              .collect(Collectors.toMap(
	                Map.Entry::getKey, 
	                Map.Entry::getValue, 
	                (e1, e2) -> e1, 
	                LinkedHashMap::new
	              ));
	}
	
	public static <K, V extends Comparable<? super V>> Map<K, V> sortByKey(Map<K, V> map) {
	    return map.entrySet()
	              .stream()
	              .sorted(Map.Entry.comparingByKey(Collections.reverseOrder())) // sort in descending order
	              .collect(Collectors.toMap(
	                Map.Entry::getKey, 
	                Map.Entry::getValue, 
	                (e1, e2) -> e1, 
	                LinkedHashMap::new
	              ));
	}
	
	public static <K, V extends Comparable<? super V>> Map<K, V> sortByValueAscending(Map<K, V> map) {
	    return map.entrySet()
	              .stream()
	              .sorted(Map.Entry.comparingByValue()) // sort in ascending order
	              .collect(Collectors.toMap(
	                Map.Entry::getKey, 
	                Map.Entry::getValue, 
	                (e1, e2) -> e1, 
	                LinkedHashMap::new
	              ));
	}
	
	public static <K, V extends Comparable<? super V>> Map<K, V> sortByKeyAscending(Map<K, V> map) {
	    return map.entrySet()
	              .stream()
	              .sorted(Map.Entry.comparingByKey(Collections.reverseOrder().reversed())) // sort in ascending order
	              .collect(Collectors.toMap(
	                Map.Entry::getKey, 
	                Map.Entry::getValue, 
	                (e1, e2) -> e1, 
	                LinkedHashMap::new
	              ));
	}
	
	public static <K, V> Map<K, V> getTopNbyValue(Map<K, V> sortedMap, int N){
		Map<K, V> topNmap = new LinkedHashMap<>();
		int counter = 0;
		for(Map.Entry<K, V> entry: sortedMap.entrySet()){
			topNmap.put(entry.getKey(), entry.getValue());
			counter++;
			if(counter == N){
				break;
			}
		}
		return topNmap;
	}
	
	public static Map<String, Integer> getTopNbyValue_StringKeys(Map<String, Integer> predicates_counts, int N){
		Map<String, Integer> topNmap = new HashMap<>();
		int counter = 0;
		for(Map.Entry<String, Integer> entry: GenericUtils.sortByValue(predicates_counts).entrySet()){  //sorting once more to make sure
			topNmap.put(entry.getKey(), entry.getValue());
			counter++;
			if(counter == N){
				break;
			}
		}
		return topNmap;
	}
	
	public static <T, E> Set<T> getKeysByValue(Map<T, E> map, E value) {
	    return map.entrySet()
	              .stream()
	              .filter(entry -> Objects.equals(entry.getValue(), value))
	              .map(Map.Entry::getKey)
	              .collect(Collectors.toSet());
	}
	
	public static <K,V> Object getKeyFromValue(Map<K,V> map, Object value) {
		//System.out.println("........................." + value);
	    for(Object key : map.keySet()){
	      if(map.get(key).equals(value)){
	    	  //System.out.println("..................." + value + " " + key);
	        return key;
	      }
	    }
	    return null;
	  }	
	/*public static <K, V> String prettyPrintMap(Map<K, V> content,
	String kvSeparator, String twoKvSeparator) {
	StringBuilder s = new StringBuilder();
	DecimalFormat df = new DecimalFormat("#.##");
	if (content == null || content.size() < 1)
		return s.toString();
	for (Entry<K, V> e : content.entrySet()) {
		s.append(twoKvSeparator).append(classIDs.getKeyFromValue(Integer.parseInt(e.getKey().toString().replace(".0", "")))).append(kvSeparator)
			.append(df.format(e.getValue()));
	}
	return s.substring(twoKvSeparator.length());
}*/
}
