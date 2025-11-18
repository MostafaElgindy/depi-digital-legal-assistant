import os
import sys
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from model import setup_chat_engine, create_vector_store_and_index, setup_chroma_collection, chat_with_memory
from ingest import create_collection_from_pdf
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/chat")
async def chat_with_pdf(query_request: str = Query(...)):
    try:
        logger.info(f"Received query: {query_request}")
        chroma_collection = setup_chroma_collection()
        index = create_vector_store_and_index(chroma_collection)
        chat_engine, chat_history = setup_chat_engine(index)

        response = chat_with_memory(chat_engine, chat_history, query_request)
        logger.info(f"Response generated: {response}")
        return {"response": str(response)}
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Save the uploaded PDF file to a temporary location
    pdf_file_path = f"./temp/{file.filename}"  # Temporary path for the uploaded file
    try:
        os.makedirs("./temp", exist_ok=True)  # Ensure the temp directory exists
        with open(pdf_file_path, "wb") as f:
            f.write(await file.read())
        
        # Process the PDF to create a collection
        create_collection_from_pdf(pdf_file_path)

        # Clean up the temporary file
        os.remove(pdf_file_path)

        return JSONResponse(content={"message": f"Collection created from '{file.filename}' successfully."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Ensure the temporary file is removed in case of an error
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
