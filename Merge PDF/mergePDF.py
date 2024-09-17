import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import fitz  # PyMuPDF
from PIL import Image
import base64
from streamlit_sortables import sort_items  # Add this import

st.set_page_config(page_title="PDF Merger App", page_icon=":page_facing_up:", layout="wide")

def merge_pdfs(pdf_files):
    merger = PdfWriter()
    for pdf in pdf_files:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            merger.add_page(page)
    
    output = io.BytesIO()
    merger.write(output)
    return output.getvalue()

def get_pdf_preview(pdf_file):
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    first_page = pdf_document.load_page(0)
    pix = first_page.get_pixmap(matrix=fitz.Matrix(2, 2))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

st.title("PDF Merger App")

uploaded_files = st.file_uploader("Choose PDF files", accept_multiple_files=True, type="pdf")

if 'file_order' not in st.session_state:
    st.session_state.file_order = []

if uploaded_files:
    if st.session_state.file_order != uploaded_files:
        st.session_state.file_order = uploaded_files.copy()

    st.subheader("Reorder PDFs")
    
    # Create a list of file names for sorting
    file_names = [file.name for file in st.session_state.file_order]
    
    # Use sort_items for reordering
    sorted_names = sort_items(file_names, key="pdf_list")
    
    # Update file order based on sorting
    if sorted_names:
        st.session_state.file_order = [
            file for file in st.session_state.file_order 
            if file.name in sorted_names
        ]
        st.session_state.file_order.sort(key=lambda x: sorted_names.index(x.name))

    # Display previews
    cols = st.columns(4)  # Adjust the number of columns as needed
    for index, file in enumerate(st.session_state.file_order):
        with cols[index % 4]:  # This will cycle through the columns
            st.write(file.name)
            preview_img = get_pdf_preview(file)
            st.image(preview_img, use_column_width=True)
        file.seek(0)  # Reset file pointer

    if st.button("Merge PDFs"):
        merged_pdf = merge_pdfs(st.session_state.file_order)
        
        # Create a download button for the merged PDF
        st.download_button(
            label="Download Merged PDF",
            data=merged_pdf,
            file_name="merged.pdf",
            mime="application/pdf"
        )
else:
    st.info("Please upload PDF files to merge.")