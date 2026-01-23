"""
File conversion utilities
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Tuple
from PIL import Image
import PyPDF2
from docx import Document
import json
import csv
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Supported formats mapping
FORMAT_CONVERSIONS = {
    # Images
    'jpg': ['png', 'webp', 'bmp', 'pdf'],
    'jpeg': ['png', 'webp', 'bmp', 'pdf'],
    'png': ['jpg', 'webp', 'bmp', 'pdf'],
    'webp': ['jpg', 'png', 'bmp', 'pdf'],
    'bmp': ['jpg', 'png', 'webp', 'pdf'],
    'svg': ['png', 'jpg', 'pdf'],
    
    # Documents
    'pdf': ['docx', 'txt', 'jpg', 'png'],
    'docx': ['pdf', 'txt'],
    'doc': ['pdf', 'txt'],
    'txt': ['pdf', 'docx'],
    'pptx': ['pdf'],
    'xlsx': ['csv', 'pdf'],
    'csv': ['xlsx', 'json', 'xml'],
    
    # Audio
    'mp3': ['wav', 'aac', 'ogg', 'flac'],
    'wav': ['mp3', 'aac', 'ogg', 'flac'],
    'aac': ['mp3', 'wav', 'ogg', 'flac'],
    'ogg': ['mp3', 'wav', 'aac', 'flac'],
    'flac': ['mp3', 'wav', 'aac', 'ogg'],
    
    # Video
    'mp4': ['mkv', 'avi', 'mov', 'gif'],
    'mkv': ['mp4', 'avi', 'mov'],
    'avi': ['mp4', 'mkv', 'mov'],
    'mov': ['mp4', 'mkv', 'avi'],
    
    # Archives
    'zip': ['tar'],
    'tar': ['zip'],
    
    # Data
    'json': ['csv', 'xml', 'txt'],
    'xml': ['json', 'csv', 'txt'],
    'md': ['html', 'pdf'],
    'html': ['pdf', 'txt'],
}


def get_file_extension(filename: str) -> str:
    """Get file extension without dot"""
    return Path(filename).suffix.lower().lstrip('.')


def get_supported_formats(file_extension: str) -> List[str]:
    """Get list of supported conversion formats for a file type"""
    return FORMAT_CONVERSIONS.get(file_extension.lower(), [])


class FileConverter:
    def __init__(self, temp_dir: str = '/tmp/converter'):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def convert(self, input_file: str, output_format: str) -> Optional[str]:
        """Main conversion function"""
        input_ext = get_file_extension(input_file)
        
        # Route to appropriate converter
        if input_ext in ['jpg', 'jpeg', 'png', 'webp', 'bmp']:
            return self._convert_image(input_file, output_format)
        elif input_ext == 'svg':
            return self._convert_svg(input_file, output_format)
        elif input_ext in ['pdf']:
            return self._convert_pdf(input_file, output_format)
        elif input_ext in ['docx', 'doc']:
            return self._convert_document(input_file, output_format)
        elif input_ext in ['mp3', 'wav', 'aac', 'ogg', 'flac']:
            return self._convert_audio(input_file, output_format)
        elif input_ext in ['mp4', 'mkv', 'avi', 'mov']:
            return self._convert_video(input_file, output_format)
        elif input_ext in ['json', 'csv', 'xml']:
            return self._convert_data(input_file, output_format)
        else:
            logger.error(f"Unsupported format: {input_ext}")
            return None
    
    def _convert_image(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert image files"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            if output_format == 'pdf':
                # Convert image to PDF
                img = Image.open(input_file)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(output_file, 'PDF')
            else:
                # Convert between image formats
                img = Image.open(input_file)
                if output_format in ['jpg', 'jpeg'] and img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                img.save(output_file, output_format.upper())
            
            return output_file
        except Exception as e:
            logger.error(f"Image conversion error: {e}")
            return None
    
    def _convert_svg(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert SVG files using ImageMagick"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            # Use ImageMagick convert command
            cmd = ['convert', '-background', 'none', input_file, output_file]
            subprocess.run(cmd, check=True, capture_output=True)
            
            return output_file
        except Exception as e:
            logger.error(f"SVG conversion error: {e}")
            return None
    
    def _convert_pdf(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert PDF files"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            if output_format == 'txt':
                # Extract text from PDF
                with open(input_file, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text() + '\n\n'
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            
            elif output_format in ['jpg', 'png']:
                # Convert PDF to image (first page)
                cmd = [
                    'convert', '-density', '300',
                    f'{input_file}[0]', '-quality', '90',
                    output_file
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            
            elif output_format == 'docx':
                # PDF to DOCX using pandoc
                cmd = ['pandoc', input_file, '-o', output_file]
                subprocess.run(cmd, check=True, capture_output=True)
            
            return output_file
        except Exception as e:
            logger.error(f"PDF conversion error: {e}")
            return None
    
    def _convert_document(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert document files"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            if output_format == 'pdf':
                # Use LibreOffice for DOCX to PDF
                cmd = [
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', os.path.dirname(output_file), input_file
                ]
                subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            
            elif output_format == 'txt':
                # Extract text from DOCX
                doc = Document(input_file)
                text = '\n\n'.join([para.text for para in doc.paragraphs])
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            
            return output_file
        except Exception as e:
            logger.error(f"Document conversion error: {e}")
            return None
    
    def _convert_audio(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert audio files using FFmpeg"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            cmd = ['ffmpeg', '-i', input_file, '-y', output_file]
            subprocess.run(cmd, check=True, capture_output=True, timeout=300)
            
            return output_file
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return None
    
    def _convert_video(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert video files using FFmpeg"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            
            if output_format == 'gif':
                # Convert to GIF with optimization
                cmd = [
                    'ffmpeg', '-i', input_file, '-vf',
                    'fps=10,scale=480:-1:flags=lanczos',
                    '-c:v', 'gif', '-y', output_file
                ]
            else:
                # Standard video conversion
                cmd = ['ffmpeg', '-i', input_file, '-y', output_file]
            
            subprocess.run(cmd, check=True, capture_output=True, timeout=600)
            
            return output_file
        except Exception as e:
            logger.error(f"Video conversion error: {e}")
            return None
    
    def _convert_data(self, input_file: str, output_format: str) -> Optional[str]:
        """Convert data files (JSON, CSV, XML)"""
        try:
            output_file = input_file.rsplit('.', 1)[0] + f'.{output_format}'
            input_ext = get_file_extension(input_file)
            
            # Load data based on input format
            data = None
            if input_ext == 'json':
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif input_ext == 'csv':
                with open(input_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
            elif input_ext == 'xml':
                tree = ET.parse(input_file)
                root = tree.getroot()
                # Simple XML to dict conversion
                data = self._xml_to_dict(root)
            
            # Save in output format
            if output_format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif output_format == 'csv':
                if isinstance(data, list) and len(data) > 0:
                    with open(output_file, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            elif output_format == 'xml':
                root = ET.Element('root')
                self._dict_to_xml(root, data)
                tree = ET.ElementTree(root)
                tree.write(output_file, encoding='utf-8', xml_declaration=True)
            elif output_format == 'txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
            return output_file
        except Exception as e:
            logger.error(f"Data conversion error: {e}")
            return None
    
    def _xml_to_dict(self, element):
        """Convert XML element to dictionary"""
        result = {}
        for child in element:
            if len(child) == 0:
                result[child.tag] = child.text
            else:
                result[child.tag] = self._xml_to_dict(child)
        return result
    
    def _dict_to_xml(self, parent, data):
        """Convert dictionary to XML elements"""
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, str(key))
                if isinstance(value, (dict, list)):
                    self._dict_to_xml(child, value)
                else:
                    child.text = str(value)
        elif isinstance(data, list):
            for item in data:
                child = ET.SubElement(parent, 'item')
                self._dict_to_xml(child, item)
        else:
            parent.text = str(data)