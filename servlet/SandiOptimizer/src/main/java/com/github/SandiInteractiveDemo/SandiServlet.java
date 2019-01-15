package com.github.SandiInteractiveDemo;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.logging.Logger;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.NamingException;
import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import models.ILPBased;

/**
 * Servlet implementation class SandiServlet
 */
public class SandiServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
	
	private final static Logger LOGGER = Logger.getLogger(SandiServlet.class.getName());
	
	private ILPBased ilp = null;
	
	private String model_path = null;
      
    public SandiServlet() {
        super();
    }

	public void init(ServletConfig config) throws ServletException {

    	LOGGER.info("Loading Word2Vec Model");
    	try {
            Context init_context = new InitialContext();
            model_path = (String) init_context.lookup("java:comp/env/model_path");
            
            LOGGER.info("Loading model from path " + model_path);
            
            ilp = new ILPBased(model_path);
		} catch (IOException e) {
			e.printStackTrace();
		} 
    	catch (NamingException e) {
			e.printStackTrace();
		}
    	
    	LOGGER.info("Finished Loading Word2Vec Model");
	}

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		PrintWriter writer;
        String err = "";
        String work_dir = "";
        String path_to_alignment = "";

        int num_images;
        
        LOGGER.info("Received GET Request to Sandi Alignment server");

        /* Read request parameters */
        work_dir    = request.getParameter("work_dir");
        
        try {
        	num_images  = Integer.parseInt(request.getParameter("num_images"));
        } catch(NumberFormatException e)  {
        	num_images  = 0;
        }
        
        if (work_dir == null) {

              err = "Parameter \"work_dir\" is missing.";
              
              LOGGER.warning(err);

              response.sendError(HttpServletResponse.SC_BAD_REQUEST, err);

        } else if (!new File(work_dir).isDirectory()) {

              err = String.format("Parameter \"work_dir\": \"%s\" is not a valid path. Must be a full path.", work_dir);

              LOGGER.warning(err);

              response.sendError(HttpServletResponse.SC_BAD_REQUEST, err);

        } else {

              LOGGER.info(String.format("Parameters - work_dir: %s, num_images: %d", work_dir, num_images));

              LOGGER.info("Start alignment");

              /* TODO: Start alignment here */

              LOGGER.info("Finished alignment");

              response.setContentType("application/json");
              writer = response.getWriter();
              writer.write(String.format("{\"aligned\": \"%s\"}", path_to_alignment));
              writer.close();
  
              LOGGER.info("Finished GET Request to Sandi Alignment server");

        }
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
