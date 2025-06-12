import argparse
import os
import json
from pageindex import *

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process PDF or TXT document and generate structure')
    parser.add_argument('--doc_path', type=str, help='Path to the PDF or TXT file')
    parser.add_argument('--pdf_path', type=str, help='Path to the PDF file (deprecated, use --doc_path)')
    parser.add_argument('--model', type=str, default='gpt-4o-2024-11-20', help='Model to use')
    parser.add_argument('--toc-check-pages', type=int, default=20, 
                      help='Number of pages to check for table of contents')
    parser.add_argument('--max-pages-per-node', type=int, default=20,
                      help='Maximum number of pages per node')
    parser.add_argument('--max-tokens-per-node', type=int, default=20000,
                      help='Maximum number of tokens per node')
    parser.add_argument('--if-add-node-id', type=str, default='yes',
                      help='Whether to add node id to the node')
    parser.add_argument('--if-add-node-summary', type=str, default='no',
                      help='Whether to add summary to the node')
    parser.add_argument('--if-add-doc-description', type=str, default='yes',
                      help='Whether to add doc description to the doc')
    parser.add_argument('--if-add-node-text', type=str, default='no',
                      help='Whether to add text to the node')
    
    # Add TXT processing arguments
    parser.add_argument('--txt-method', type=str, default='token', choices=['char', 'token'],
                      help='TXT segmentation method: "char" or "token" (default: token)')
    parser.add_argument('--txt-tokens-per-page', type=int, default=1024,
                      help='Number of tokens per page for TXT files (default: 1024)')
    parser.add_argument('--txt-chars-per-page', type=int, default=2048,
                      help='Number of characters per page for TXT files (default: 2048)')
    parser.add_argument('--txt-tokenizer', type=str, default='gpt2',
                      help='Tokenizer encoding name for TXT files (default: gpt2)')
    parser.add_argument('--txt-chunk-overlap', type=int, default=5,
                      help='Token overlap between chunks for TXT files (default: 5)')
    
    args = parser.parse_args()
    
    # Determine document path (support both --doc_path and --pdf_path for backward compatibility)
    doc_path = args.doc_path or args.pdf_path
    if not doc_path:
        parser.error("Either --doc_path or --pdf_path is required")
    
    if not os.path.exists(doc_path):
        print(f"Error: File not found: {doc_path}")
        exit(1)
    
    # Check if file type is supported
    supported_extensions = ['.pdf', '.txt']
    file_extension = os.path.splitext(doc_path)[1].lower()
    if file_extension not in supported_extensions:
        print(f"Error: Unsupported file type '{file_extension}'. Supported types: {supported_extensions}")
        exit(1)
        
    # Configure options
    opt = config(
        model=args.model,
        toc_check_page_num=args.toc_check_pages,
        max_page_num_each_node=args.max_pages_per_node,
        max_token_num_each_node=args.max_tokens_per_node,
        if_add_node_id=args.if_add_node_id,
        if_add_node_summary=args.if_add_node_summary,
        if_add_doc_description=args.if_add_doc_description,
        if_add_node_text=args.if_add_node_text,
        txt_page_method=args.txt_method,
        txt_tokens_per_page=args.txt_tokens_per_page,
        txt_chars_per_page=args.txt_chars_per_page,
        txt_tokenizer=args.txt_tokenizer,
        txt_chunk_overlap=args.txt_chunk_overlap
    )


    # Process the document
    toc_with_page_number = page_index_main(doc_path, opt)
    print('Parsing done, saving to file...')
    
    # Save results
    doc_name = os.path.splitext(os.path.basename(doc_path))[0]    
    os.makedirs('./results', exist_ok=True)
    
    with open(f'./results/{doc_name}_structure.json', 'w', encoding='utf-8') as f:
        json.dump(toc_with_page_number, f, indent=2)